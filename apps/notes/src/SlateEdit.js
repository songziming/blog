// 使用 slate.js 定制的富文本编辑器

import { createEditor, Transforms, Editor, Element } from 'slate';
import { Slate, Editable, withReact } from 'slate-react';
import { useCallback, useState, useMemo } from 'react';

import { SlateCodeBlock, SlateCodeLine } from './SlateCode';

import './Editor.css';



/*
// 不同类型的 block 有不同的属性，这里取并集
// 这样不管切换到什么类型，属性字段都存在
const kBlockDefs = {
  type: 'para',
  lang: 'cpp', // 可以自动分析用户习惯，预测可能的语言，或者使用上一个代码块的语言
  level: 1,
};
*/




// 自定义命令
const MyEditor = {

  toggleBold: (editor) => {
    const isBold = Editor.marks(editor)?.bold || false;
    Editor.addMark(editor, 'bold', !isBold);
    // 也可以用 removeMark
  },

  toggleCode: (editor) => {
    const [match] = Editor.nodes(editor, {
      match: n => n.type === 'codeblock',
    });

    if (!match) {
      // 将文本包一层 codeblock
      Transforms.wrapNodes(editor, { type: 'codeblock', lang: 'py' }, {
        match: n => Element.isElement(n) && (n.type === 'codeline' || n.type === 'paragraph'),
        split: true,
      });
      // 变成 codeline
      Transforms.setNodes(editor, { type: 'codeline' }, {
        match: n => Element.isElement(n) && (n.type === 'codeline' || n.type === 'paragraph')
      });
      // 去掉样式
      Transforms.setNodes(editor, { bold: false }, {
        match: n => !Element.isElement(n)
      });
    } else {
      // 将 codeblock 拆开
      Transforms.unwrapNodes(editor, {
        match: n => Element.isElement(n) && n.type === 'codeblock'
      });
      // 里面的 codeline 换成普通段落
      Transforms.setNodes(editor,
        { type: 'paragraph' },
        { match: n => Element.isElement(n) && n.type === 'codeline' }
      );
    }
  },

  // 获取当前代码块的高亮语言
  getLang: (editor) => {
    const [code] = Editor.nodes(editor, {
      match: n => n.type === 'code',
    });
    return code?.lang || 'cpp';
  },

  setLang: (editor, lang) => {
    // const [code] = Editor.nodes(editor, {
    //   match: n => n.type === 'code',
    // });
    Transforms.setNodes(editor,
      { lang },
      { match: n => Element.isElement(n) && Editor.isBlock(editor, n) && n.type === 'code' }
    );
  },

};




// 默认块
const DefaultElement = props => {
  return <p className="para" {...props.attributes}>{props.children}</p>;
};



// Inline 元素
const Leaf = props => <span {...props.attributes} style={{
  fontWeight: props.leaf.bold ? 'bold' : 'normal',
  fontStyle: props.leaf.italic ? 'italic' : 'normal',
  ...(props.leaf.strike && { textDecoration: 'line-through' }),
}}>{props.children}</span>;



// 默认文档内容
const kINITIALVALUE = [{
  type: 'paragraph',
  children: [{ text: 'A line of text in a paragraph.' }],
}];

const SlateEdit = () => {
  const [editor] = useState(withReact(createEditor()));

  // 渲染段落元素的回调函数
  const renderElement = useCallback(props => {
    switch (props.element.type) {
    case 'codeblock':  return <SlateCodeBlock {...props} />;
    case 'codeline':  return <SlateCodeLine {...props} />;
    default:  return <DefaultElement {...props} />;
    }
  }, []);

  // 渲染 Inline 元素的回调函数
  const renderLeaf = useCallback(props => <Leaf {...props} />, []);

  const handleKeyDown = useCallback(ev => {
    // 如果使用中文输入法，只有空格退格删除回车能显示正确的 key，其他的均显示 Process
    // 但是输入法模式下使用 ctrl、alt 等组合键，则可以正确显示 key
    // console.log('keydown', ev.key);

    if (ev.key === 'Tab') {
      ev.preventDefault();
      Editor.insertText(editor, '\t');
      return;
    }

    if (!ev.ctrlKey) {
      return;
    }

    switch (ev.key) {
      case '`': {
        ev.preventDefault();
        MyEditor.toggleCode(editor);
        // const [match] = Editor.nodes(editor, {
        //   match: n => n.type === 'code',
        // });
        // Transforms.setNodes(editor,
        //   { type: match ? 'paragraph' : 'code' },
        //   { match: n => Element.isElement(n) && Editor.isBlock(editor, n) }
        // );
        break;
      }
      case 'b': {
        ev.preventDefault();
        MyEditor.toggleBold(editor);
        // const isBold = Editor.marks(editor)?.bold || false;
        // Editor.addMark(editor, 'bold', !isBold);
        break;
      }
      default:
        break;
    }
  }, [editor]);



  const handleChange = useCallback(value => {
    // 光标选择区的变化不算数据变更
    const isAstChange = editor.operations.some(op => 'set_selection' !== op.type);
    console.log('change', isAstChange);
    if (!isAstChange) {
      return;
    }

    // TODO 标记为 dirty
    const content = JSON.stringify(value);
    localStorage.setItem('content', content);
  }, [editor]);



  // const initialValue = [{
  //   type: 'paragraph',
  //   children: [{ text: 'A line of text in a paragraph.' }],
  // }];

  const initialValue = useMemo(() => {
    const content = localStorage.getItem('content');
    if (!content) {
      return kINITIALVALUE;
    }
    const obj = JSON.parse(content);
    if (!obj) {
      return kINITIALVALUE;
    }
    return obj;
  }, []);


  return <Slate editor={editor} initialValue={initialValue} onChange={handleChange}>
    <div className="fullscreen">
      <Editable style={{ height: '100%' }}
        renderElement={renderElement}
        renderLeaf={renderLeaf}
        onKeyDown={handleKeyDown} />
    </div>
  </Slate>;
};

export default SlateEdit;
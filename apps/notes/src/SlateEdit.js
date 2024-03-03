// 使用 slate.js 定制的富文本编辑器

import { createEditor, Transforms, Editor, Element } from 'slate';
import { Slate, Editable, withReact } from 'slate-react';
import { useCallback, useState } from 'react';

import './Editor.css';




// 代码块
const CodeElement = props => {
  return <pre className="para" {...props.attributes}>
    <code>{props.children}</code>
  </pre>;
};

// 默认块
const DefaultElement = props => {
  return <p className="para" {...props.attributes}>{props.children}</p>;
};



// Inline 元素
const Leaf = props => <span {...props.attributes} style={{
  fontWeight: props.leaf.bold ? 'bold' : 'normal'
}}>{props.children}</span>;





// 默认文档内容
const initialValue = [{
  type: 'paragraph',
  children: [{ text: 'A line of text in a paragraph.' }],
}];

const SlateEdit = () => {
  const [editor] = useState(withReact(createEditor()));

  // 渲染段落元素的回调函数
  const renderElement = useCallback(props => {
    switch (props.element.type) {
    case 'code':  return <CodeElement {...props} />;
    default:  return <DefaultElement {...props} />;
    }
  }, []);

  // 渲染 Inline 元素的回调函数
  const renderLeaf = useCallback(props => <Leaf {...props} />, []);

  const handleKeyDown = useCallback(ev => {
    // 如果使用中文输入法，只有空格退格删除回车能显示正确的 key，其他的均显示 Process
    // 但是输入法模式下使用 ctrl、alt 等组合键，则可以正确显示 key
    console.log('keydown', ev.key);

    if (!ev.ctrlKey) {
      return;
    }

    switch (ev.key) {
      case '`': {
        // 将这个段落改为代码块，或者改回文本
        ev.preventDefault();
        const [match] = Editor.nodes(editor, {
          match: n => n.type === 'code',
        });
        Transforms.setNodes(editor,
          { type: match ? 'paragraph' : 'code' },
          { match: n => Element.isElement(n) && Editor.isBlock(editor, n) }
        );
        break;
      }
      case 'b': {
        ev.preventDefault();
        // console.log(Editor.marks(editor).bold);
        const isBold = Editor.marks(editor)?.bold || false;
        Editor.addMark(editor, 'bold', !isBold);
        break;
      }
      default:
        break;
    }
  }, [editor]);

  return <Slate editor={editor} initialValue={initialValue}>
    <div className="fullscreen">
      <Editable style={{ height: '100%' }}
        renderElement={renderElement}
        renderLeaf={renderLeaf}
        onKeyDown={handleKeyDown} />
    </div>
  </Slate>;
};

export default SlateEdit;

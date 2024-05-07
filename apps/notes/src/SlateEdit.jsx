// 使用 slate.js 定制的富文本编辑器

import { createEditor, Editor } from 'slate';
import { withHistory } from 'slate-history';
import { Slate, Editable, withReact } from 'slate-react';
import { useCallback, useMemo } from 'react';

import { renderElement, renderLeaf } from './nodes.jsx';

import SlateToolBar from './SlateToolBar';

import './Editor.css';




// 自定义插件，重写 editor 的成员函数
const withInlines = editor => {
  const { isInline, insertNode } = editor;

  editor.isInline = element => [
    'codeline', 'codespan', 'mathspan', 'linkspan'
  ].includes(element.type) || isInline(element);

  editor.insertText = text => {
    // console.log('inserting', text);
    insertNode({text: text, script: 'cjk'});
  };

  return editor;
};




// 核心编辑器
const SlateEdit = () => {
  const editor = useMemo(() => withInlines(withHistory(withReact(createEditor()))), []);
  // const editor = useMemo(() => withHistory(withReact(createEditor())), []);
  // const editor = useMemo(() => withReact(createEditor()), []);

  const initialValue = useMemo(() => {
    const content = localStorage.getItem('content');
    return JSON.parse(content) || [{
      type: 'paragraph',
      children: [{ text: 'A line of text in a paragraph.' }],
    }];
  }, []);

  const handleChange = useCallback(value => {
    // 光标选择区的变化不算数据变更
    const isAstChange = editor.operations.some(op => 'set_selection' !== op.type);
    // console.log('change', isAstChange);
    if (!isAstChange) {
      return;
    }

    // TODO 标记为 dirty
    const content = JSON.stringify(value);
    localStorage.setItem('content', content);
  }, [editor]);

  const handleKeyDown = useCallback(ev => {
    // 如果使用中文输入法，只有空格退格删除回车能显示正确的 key，其他的均显示 Process
    // 但是输入法模式下使用 ctrl、alt 等组合键，则可以正确显示 key
    // console.log('keydown', ev.key, ev);

    // 检测 ctrl 组合键
    if (ev.ctrlKey) {
      switch (ev.key) {
      case 'b': console.log('bold'); break; // cmd.toggleBold(editor);
      case 'i': console.log('italic'); break;
      case 'u': console.log('underline'); break;
      case '`': console.log('codeblock'); break; // cmd.toggleCode(editor);
      default: break;
      }
      return;
    }

    // 检测 shift 组合键（大部分是大写/上标）
    if (ev.shiftKey) {
      if ('Enter' === ev.key) {
        ev.preventDefault();
        Editor.insertText(editor, '\n');
        return;
      }
    }

    if (ev.key === 'Tab') {
      ev.preventDefault();
      Editor.insertText(editor, '\t');
      return;
    }

    // ev.preventDefault();
    // Editor.insertNode(editor, {text: ev.key});
  }, [editor]);


  return <Slate editor={editor} initialValue={initialValue} onChange={handleChange}>
    <div className="fullscreen">
      <SlateToolBar />
      <Editable className="editable"
        renderElement={renderElement}
        renderLeaf={renderLeaf}
        onKeyDown={handleKeyDown} />
    </div>
  </Slate>;
};

export default SlateEdit;

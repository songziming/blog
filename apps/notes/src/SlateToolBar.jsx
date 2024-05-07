import { useCallback } from 'react';
import { useSlate } from 'slate-react';
import { Editor } from 'slate';
import * as cmd from './SlateCommands';


// 编辑器的工具栏，各种样式设置按钮
// 此模块只负责渲染工具栏 UI，对文档数据模型的修改交给 SlateCommands.js


const SlateToolBar = () => {
  const editor = useSlate();

  // 测试函数，遍历 AST
  const showAST = useCallback(() => {
    const all_nodes = Editor.nodes(editor, {at:[]});
    for (const [node, path] of all_nodes) {
      if ('type' in node) {
        console.log(`node ${node.type} at ${path}`, node);
      } else if ('text' in node) {
        let marks = Object.keys(node).filter(s => s !== 'text');
        console.log(`text ${path} "${node.text}", marks (${marks})`);
      } else {
        console.log('Editor', path);
      }
    }
  }, [editor]);

  const cleanAST = useCallback(() => cmd.clearAll(editor), [editor]);

  const dropMarks = useCallback(() => cmd.unsetMarks(editor, ['bold', 'italic', 'underline']), [editor]);

  const convParagraph = useCallback(() => cmd.toParagraph(editor), [editor]);
  const convCodeBlock = useCallback(() => cmd.toCodeBlock(editor), [editor]);
  const convListBlock = useCallback(() => cmd.toListBlock(editor), [editor]);
  const convHeader1 = useCallback(() => cmd.toHeader(editor, 1), [editor]);
  const convHeader2 = useCallback(() => cmd.toHeader(editor, 2), [editor]);
  const convHeader3 = useCallback(() => cmd.toHeader(editor, 3), [editor]);

  const toggleBold = useCallback(() => cmd.toggleMark(editor, 'bold'), [editor]);
  const toggleItalic = useCallback(() => cmd.toggleMark(editor, 'italic'), [editor]);
  const toggleUnderline = useCallback(() => cmd.toggleMark(editor, 'underline'), [editor]);

  return <div className="toolbar">
    <span>Tools: </span>
    <button onClick={showAST}>show</button>
    <button onClick={cleanAST}>clear</button>
    <button onClick={dropMarks}>drop</button>
    <button onClick={convParagraph}>para</button>
    <button onClick={convHeader1}>H1</button>
    <button onClick={convHeader2}>H2</button>
    <button onClick={convHeader3}>H3</button>
    <button onClick={convCodeBlock}>code</button>
    <button onClick={convListBlock}>list</button>
    <button onClick={toggleBold}>B</button>
    <button onClick={toggleItalic}>I</button>
    <button onClick={toggleUnderline}>U</button>
  </div>;
};

export default SlateToolBar;

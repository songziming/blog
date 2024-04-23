import { useCallback } from 'react';
import { useSlate } from 'slate-react';
import { Editor } from 'slate';
import * as cmd from './SlateCommands';


// 编辑器的工具栏，各种样式设置按钮
// 此模块只负责渲染工具栏 UI，对文档数据模型的修改交给 SlateCommands.js


const SlateToolBar = () => {
  const editor = useSlate();

  // 测试函数，使用 transform 检查 AST
  const showAST = useCallback(() => {
    // Transforms.setNodes(editor, {}, {
    //   match: (n) => {
    //     console.log(n);
    //     return false;
    //   },
    // });

    // 遍历所有的非叶子节点
    const all_nodes = Editor.nodes(editor, {at:[]});
    for (const [node, path] of all_nodes) {
      if (!('type' in node)) {
        // 没有 type，说明这是 Editor
        console.log('Editor');
      } else {
        console.log(`node ${node.type} at ${path}`, node);
      }
    }
  }, [editor]);

  const dropMarks = useCallback(() => cmd.unsetMarks(editor, ['bold', 'italic', 'underline']), [editor]);

  const convParagraph = useCallback(() => cmd.toParagraph(editor), [editor]);
  const convCodeBlock = useCallback(() => cmd.toCodeBlock(editor), [editor]);
  const convListBlock = useCallback(() => cmd.toListBlock(editor), [editor]);

  const toggleBold = useCallback(() => cmd.toggleMark(editor, 'bold'), [editor]);
  const toggleItalic = useCallback(() => cmd.toggleMark(editor, 'italic'), [editor]);
  const toggleUnderline = useCallback(() => cmd.toggleMark(editor, 'underline'), [editor]);

  return <div className="toolbar">
    <span>Tools: </span>
    <button onClick={showAST}>show</button>
    <button onClick={dropMarks}>drop</button>
    <button onClick={convParagraph}>para</button>
    <button onClick={convCodeBlock}>code</button>
    <button onClick={convListBlock}>list</button>
    <button onClick={toggleBold}>B</button>
    <button onClick={toggleItalic}>I</button>
    <button onClick={toggleUnderline}>U</button>
  </div>;
};

export default SlateToolBar;

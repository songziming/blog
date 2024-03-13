import { useCallback } from 'react';
import { useSlate } from 'slate-react';
import { Transforms } from 'slate';
import * as cmd from './SlateCommands';

const SlateToolBar = () => {
  const editor = useSlate();

  // 测试函数，使用 transform 检查 AST
  const showAST = useCallback(() => {
    Transforms.setNodes(editor, {}, {
      match: (n) => {
        console.log(n);
        return false;
      },
    });
  }, [editor]);

  const dropMarks = useCallback(() => cmd.dropAllMarks(editor), [editor]);

  const convParagraph = useCallback(() => cmd.toParagraph(editor), [editor]);

  const convCodeBlock = useCallback(() => cmd.toCodeBlock(editor), [editor]);

  const convListBlock = useCallback(() => cmd.toListBlock(editor), [editor]);

  return <div className="toolbar">
    <button onClick={showAST}>show</button>
    <button onClick={dropMarks}>drop</button>
    <button onClick={convParagraph}>para</button>
    <button onClick={convCodeBlock}>code</button>
    <button onClick={convListBlock}>list</button>
  </div>;
};

export default SlateToolBar;

import { Transforms } from 'slate';
import { useSlateStatic, ReactEditor } from 'slate-react';
import { useCallback } from 'react';


// // 代码行
// const SlateCodeLine = ({attributes, children}) => {
//   return <pre><code {...attributes}>{children}</code></pre>;
// };


// 代码块
const SlateCodeBlock = ({element, attributes}) => {
  // const editor = useSlateStatic();

  // const handleChangeLang = useCallback(e => {
  //   const lang = e.target.value;
  //   const path = ReactEditor.findPath(editor, element);
  //   Transforms.setNodes(editor, { lang }, { at: path });
  // }, [editor, element]);

  console.log(element);

  return <div className="block" {...attributes} contentEditable={false}>
    <pre><code contentEditable={true}>{element.content}</code></pre>
  </div>;
};


export { SlateCodeBlock };

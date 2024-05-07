import { Transforms, Text } from 'slate';
import { useSlateStatic, ReactEditor } from 'slate-react';
// import { useCallback } from 'react';

import { useCallback, useState } from "react";
import ContentEditable from "react-contenteditable";


// // 代码行
// const SlateCodeLine = ({attributes, children}) => {
//   return <pre><code {...attributes}>{children}</code></pre>;
// };


// 代码块
const SlateCodeBlock = ({element, attributes}) => {
  const editor = useSlateStatic();

  const path = ReactEditor.findPath(editor, element);

  // 必须从 element 里面取 children 元素，这样取出的才是渲染之前的 Text
  const [curCode, setCode] = useState(element.children[0].text);

  // 代码块内部输入回车无法创建新的 block，而是在 code 内部新增一行
  // 但是代码块不应该有软换行，如果输入软换行，则创建一个新的段落（无效）
  const handleChange = useCallback(ev => {
    // const nev = ev.nativeEvent;
    // if ('insertLineBreak' === nev.inputType) {
    //   console.log('this is soft line break');
    //   nev.preventDefault();
    //   nev.stopPropagation();
    //   return true;
    // }
    Transforms.setNodes(editor, {text: ev.target.value}, { at: [...path, 0], match: n=>Text.isText(n) });
    setCode(ev.target.value);
  }, [editor, path]);

  // 必须使用 data-slate-editor="true" 标记这个元素，否则 slate 会尝试自己修改 model
  return <div className="block code" {...attributes} contentEditable={false} data-slate-editor="true">
     {/*<pre><code contentEditable={true}>{element.children[0].text}</code></pre> */}
    <ContentEditable html={curCode} onChange={handleChange} data-slate-node="element" />
  </div>;
};


export { SlateCodeBlock };

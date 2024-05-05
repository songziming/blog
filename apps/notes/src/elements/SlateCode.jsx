// import { Transforms } from 'slate';
// import { useSlateStatic, ReactEditor } from 'slate-react';
// import { useCallback } from 'react';

import { useCallback, useState } from "react";
import ContentEditable from "react-contenteditable";


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

  // console.log(element.children[0]);
  // console.log(children[0]);

  // TODO 代码段正文绑定了 state，但 contentEditable 无法被 react 管理
  //      可以使用第三方代码编辑器，如 CodeMirror、Monaco

  // TODO 选中代码块内容，selection 不会体现在 slate model 中
  //      应该监听 onSelect 事件，在全局状态（react context）里记录下当前选中的 block

  const [curCode, setCode] = useState(element.children[0].text);
  const inner = <pre><code>{curCode}</code></pre>;

  const handleChange = useCallback(ev => {
    setCode({html: ev.target.value});
  });

  // 必须从 element 里面取 children 元素，这样取出的才是渲染之前的 Text
  return <div className="block" {...attributes} contentEditable={false}>
    {/* <pre><code contentEditable={true}>{element.children[0].text}</code></pre> */}
    <ContentEditable html={inner} onChange={handleChange} />
  </div>;
};


export { SlateCodeBlock };

import { Transforms } from 'slate';
import { useSlateStatic, ReactEditor } from 'slate-react';
import { useCallback } from 'react';



// 下拉列表，选择高亮语言
const LangSelector = ({onChange, value}) => {
  return <>
    <label htmlFor="lang">语言：</label>
    <select name="langs" id="langs" onChange={onChange} value={value}>
      <option value="cpp">C++</option>
      <option value="py">Python</option>
      <option value="js">JavaScript</option>
      <option value="bash">Shell</option>
    </select>
  </>
};



// 代码块
const SlateCode = ({element, attributes, children}) => {
  const editor = useSlateStatic();

  const handleChangeLang = useCallback(e => {
    const lang = e.target.value;
    const path = ReactEditor.findPath(editor, element);
    Transforms.setNodes(editor, { lang }, { at: path });
  }, [editor, element]);

  return <div className="para" {...attributes}>
    <div className="code-toolbar none-edit" contentEditable={false}>
      <LangSelector onChange={handleChangeLang} value={element.lang} />
    </div>
    <pre><code>{children}</code></pre>
  </div>;
};

export default SlateCode;

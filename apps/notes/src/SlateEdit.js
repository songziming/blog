// 使用 slate.js 定制的富文本编辑器

import { createEditor, Editor } from 'slate';
import { withHistory } from 'slate-history';
import { Slate, Editable, withReact } from 'slate-react';
import { useCallback, useMemo } from 'react';

import { SlateCodeBlock, SlateCodeLine } from './elements/SlateCode';
import { SlateListBlock, SlateListLine } from './elements/SlateList';
import { SlateParagraph, SlateHeader } from './elements/SlateParagraph';

import { SlateCodeSpan, SlateMathSpan, SlateLinkSpan } from './elements/SlateInlines';

import * as cmd from './SlateCommands';

import './Editor.css';




// 所有的 Element，不管是 block 还是 inline，都在这里渲染
const renderElement = props => {
  switch (props.element.type) {
  case 'codeblock': return <SlateCodeBlock {...props} />;
  case 'codeline':  return <SlateCodeLine  {...props} />;
  case 'listblock': return <SlateListBlock {...props} />;
  case 'listline':  return <SlateListLine  {...props} />;
  case 'paragraph': return <SlateParagraph {...props} />;
  case 'header':    return <SlateHeader    {...props} />;

  case 'codespan':  return <SlateCodeSpan  {...props} />;
  case 'mathspan':  return <SlateMathSpan  {...props} />;
  case 'linkspan':  return <SlateLinkSpan  {...props} />;

  // TODO 专门创建一个 Error 组件，用于显示错误元素的类型
  default: return <div contentEditable={false}>ERROR</div>;
  }
};


// Text 元素
const renderLeaf = props => <span {...props.attributes} style={{
  fontWeight: props.leaf.bold ? 'bold' : 'normal',
  fontStyle: props.leaf.italic ? 'italic' : 'normal',
  ...(props.leaf.strike && { textDecoration: 'line-through' }),
}}>{props.children}</span>;


// 核心编辑器
const SlateEdit = () => {
  // const editor = useMemo(() => withHistory(withReact(createEditor())), []);
  const editor = useMemo(() => withReact(createEditor()), []);

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
        cmd.toggleCode(editor);
        break;
      }
      case 'b': {
        ev.preventDefault();
        cmd.toggleBold(editor);
        break;
      }
      default:
        break;
    }
  }, [editor]);


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

// 各种类型节点的统一处理

import { Element } from 'slate';

import { SlateCodeBlock } from './elements/SlateCode';
import { SlateListBlock, SlateListLine } from './elements/SlateList';
import { SlateParagraph, SlateHeader } from './elements/SlateParagraph';

import { SlateCodeSpan, SlateMathSpan, SlateLinkSpan } from './elements/SlateInlines';



// 所有的 Element，不管是 block 还是 inline，都在这里渲染
const renderElement = props => {
  switch (props.element.type) {
  case 'codeblock': return <SlateCodeBlock {...props} />;
  case 'listblock': return <SlateListBlock {...props} />;
  case 'listline':  return <SlateListLine  {...props} />;
  case 'paragraph': return <SlateParagraph {...props} />;
  case 'header':    return <SlateHeader    {...props} />;

  // case 'codeline':  return <SlateCodeLine  {...props} />;
  case 'codespan':  return <SlateCodeSpan  {...props} />;
  case 'mathspan':  return <SlateMathSpan  {...props} />;
  case 'linkspan':  return <SlateLinkSpan  {...props} />;

  // 专门创建一个 Error 组件，用于显示错误元素的类型
  default: return <div contentEditable={false}>ERROR</div>;
  }
};


// 渲染 Text 元素
const renderLeaf = props => <span {...props.attributes} style={{
  fontWeight: props.leaf.bold ? 'bold' : 'normal',
  fontStyle: props.leaf.italic ? 'italic' : 'normal',
  ...(props.leaf.strike && { textDecoration: 'line-through' }),
  ...(props.leaf.underline && { borderBottom: '1px solid' }),
}}>{props.children}</span>;


const getText = (node) => {
    if (Element.isElement(node) && node.type === 'paragraph') {
        return node.children[0].text; // return node.code;
    } else {
        return Node.string(node);
    }
}


export {
    renderElement, renderLeaf,
    getText,
};

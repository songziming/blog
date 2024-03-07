// 一些 Inline 元素的定义


const SlateCodeSpan = ({attributes, children}) => <code {...attributes}>{children}</code>;

// 编辑形态和 render 形态不同，要么弹出 editor，要么像 Typora 一样光标进入时切换到编辑模式
const SlateMathSpan = ({attributes, children}) => <span {...attributes}>{children}</span>;

// 链接显示的文字和目标地址都要编辑，可以弹出一个编辑器，用来编辑 ref
const SlateLinkSpan = ({element, attributes, children}) => <a {...attributes} href={element.target}>{children}</a>;


export { SlateCodeSpan, SlateMathSpan, SlateLinkSpan };

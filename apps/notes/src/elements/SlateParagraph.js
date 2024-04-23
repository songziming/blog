

// 正文
const SlateParagraph = ({attributes, children}) => <p className="block" {...attributes}>{children}</p>;

// 标题
const SlateHeader = ({element, attributes, children}) => {
  const Tag = `h${element.level}`;
  return <Tag {...attributes}>{children}</Tag>;
};


export { SlateParagraph, SlateHeader };

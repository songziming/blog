// 列表有多种类型：无编号、有编号
// 列表元素可以分多级，但它们属于一个 list，而不是 list 内部套另一个 list



const SlateListLine = ({attributes, children}) => {
  return <li {...attributes}>{children}</li>;
};


const SlateListBlock = ({element, attributes, children}) => {
  const Tag = element.ordered ? 'ol' : 'ul';

  return <Tag className="block" {...attributes}>
    {children}
  </Tag>;
};


export { SlateListBlock, SlateListLine };

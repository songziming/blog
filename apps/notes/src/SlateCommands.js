import { Transforms, Editor, Element } from 'slate';


// 各种编辑都是针对选中部分


//------------------------------------------------------------------------------
// 对 Leaf 样式的改动
//------------------------------------------------------------------------------

const toggleBold = (editor) => {
  if (Editor.marks(editor)?.bold) {
    Editor.removeMark(editor, 'bold');
  }
};




//------------------------------------------------------------------------------
// 修改块类型
//------------------------------------------------------------------------------

// TODO 需要分清转换之前是什么类型，转换为什么类型，目标类型是否支持保留样式

// 将文本包一层 codeblock，原来的 block 变成 codeline，去掉样式
const toCodeBlock = (editor) => {
  Transforms.wrapNodes(editor, { type: 'codeblock', lang: 'py' }, {
    match: n => Element.isElement(n) && (n.type === 'codeline' || n.type === 'paragraph'),
    split: true,
  });
  Transforms.setNodes(editor, { type: 'codeline' }, {
    match: n => Element.isElement(n) && (n.type === 'codeline' || n.type === 'paragraph')
  });
  Transforms.setNodes(editor, { bold: false }, {
    match: n => !Element.isElement(n)
  });
}


// TODO 需要识别当前段落的类型，再有针对性地提取文字，变为普通段落
const toParagraph = (editor) => {
  // 将 codeblock 拆开
  Transforms.unwrapNodes(editor, {
    match: n => Element.isElement(n) && n.type === 'codeblock'
  });
  // 里面的 codeline 换成普通段落
  Transforms.setNodes(editor,
    { type: 'paragraph' },
    { match: n => Element.isElement(n) && n.type === 'codeline' }
  );
};



const toggleCode = (editor) => {
  const [match] = Editor.nodes(editor, {
    match: n => n.type === 'codeblock',
  });

  if (!match) {
    toCodeBlock(editor);
  } else {
    toParagraph(editor);
  }
};






export {
  toggleBold,
  toCodeBlock, toParagraph, toggleCode,
};

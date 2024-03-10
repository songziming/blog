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



// const commonConvert = (editor, dropMarks=false) => {
//   if (dropMarks) {
//     Editor.removeMark(editor, 'bold');
//     Editor.removeMark(editor, 'italic');
//     Editor.removeMark(editor, 'strikeout');
//   }

//   Transforms.setNodes(editor, {
//     type:
//   })
// };



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


const LINE_TYPES = [
  'paragraph', 'codeline', 'listline'
];


// 将正文转换为列表
// 如果选中部分包含几行 codeline，需要把这些 codeline 从 codeblock 里移除
const toListBlock = (editor) => {
  Transforms.setNodes(editor, { type: 'listline' }, {
    match: n => Element.isElement(n) && (LINE_TYPES.indexOf(n.type) !== -1),
  });
  Transforms.wrapNodes(editor, { type: 'listblock' }, {
    match: n => Element.isElement(n) && n.type === 'listline',
  });
};






export {
  toggleBold,
  toCodeBlock, toParagraph, toggleCode, toListBlock,
};

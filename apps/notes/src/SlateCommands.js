import { Transforms, Editor, Element, Text, Node } from 'slate';


// 各种编辑都是针对选中部分


//------------------------------------------------------------------------------
// 对 Leaf 样式的改动
//------------------------------------------------------------------------------

const toggleMark = (editor, mark) => {
  if (mark in (Editor.marks(editor) || {})) {
    // console.log(`removing mark ${mark}`);
    Editor.removeMark(editor, mark);
  } else {
    // console.log(`adding mark ${mark}`);
    Editor.addMark(editor, mark, true);
  }
};

const unsetMarks = (editor, marks) => {
  Transforms.unsetNodes(editor, marks, {
    match: n => Text.isText(n),
  });
};


//------------------------------------------------------------------------------
// 修改块类型
//------------------------------------------------------------------------------

// TODO 需要分清转换之前是什么类型，转换为什么类型，目标类型是否支持保留样式



// 各种类型的 block 转换为普通文本段落
// TODO codeblock 的 children 为空，代码不存储在这里
const toParagraph = (editor) => {
  Transforms.setNodes(editor,
    { type: 'paragraph' },
    { match: n => Element.isElement(n) && !editor.isInline(n) }
  );
};


// 转换为标题，还要传入级别参数
const toHeader = (editor, lv) => {
  Transforms.setNodes(editor,
    { type: 'header', level: lv },
    { match: n => Element.isElement(n) && !editor.isInline(n) }
  );
};



//------------------------------------------------------------------------------
// 代码块
//------------------------------------------------------------------------------

// slatejs 教程里，代码块是用两层 block 实现的，这样可以像正文一样编辑
// 但是仔细检查飞书 notion 等编辑器，选择区不能跨越代码块和普通文本
// 说明代码块不是用 slate element 实现的，正好可以使用 codemirror 或 monaco
// 分析飞书文档，代码块是 contentEditable=false 内部包含一个 contentEditable=true


// const 

// 代码可以有多行，多个 block 合并成一个 block
const toCodeBlock = (editor) => {
  // Transforms.unwrapNodes(editor, {
  //   at: [], // Path of Editor
  //   match: node =>
  //     !Editor.isEditor(node) &&
  //     node.children?.every(child => Editor.isBlock(editor, child)),
  //   mode: 'all', // also the Editor's children
  // });
  // // 找出选中范围包含哪些末级 block，从所在的 parent block 取出
  // Transforms.wrapNodes(editor, { type: 'codeblock', lang: 'py' }, {
  //   match: n => Element.isElement(n) && (n.type === 'codeline' || n.type === 'paragraph'),
  //   // split: true,
  // });
  // Transforms.setNodes(editor, { type: 'codeline' }, {
  //   match: n => Element.isElement(n) && (n.type === 'codeline' || n.type === 'paragraph')
  // });


  const blocks = Editor.nodes(editor, {
    match: n => Element.isElement(n),
  });
  const text = [...blocks].map(([b,p]) => Node.string(b)).join('\n');
  // console.log(text);

  Transforms.removeNodes(editor);
  Transforms.insertNodes(editor, {
    type: 'codeblock',
    children: [{text: text}], // 代码放在一个 Leaf 里面
    // content: text
  });

  // TODO 转换代码块之后，光标放在代码块内部
};



const toggleCode = (editor) => {
  const [match] = Editor.nodes(editor, {
    match: n => n.type === 'codeblock',
  });

  if (!match) {
    console.log('converting to code block');
    toCodeBlock(editor);
  } else {
    console.log('converting to paragraph');
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
  toggleMark, unsetMarks,
  toCodeBlock, toParagraph, toggleCode, toListBlock, toHeader,
};

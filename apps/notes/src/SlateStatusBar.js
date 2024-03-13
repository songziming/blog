import { useSlateSelection } from 'slate-react';


// 状态栏，显示当前光标的位置


const SlateStatusBar = () => {
  const { selection } = useSlateSelection();

  return <div>
    <p>selection: {selection}</p>
  </div>;
};

export default SlateStatusBar;

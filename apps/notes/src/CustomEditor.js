import { RecoilRoot, atom, useRecoilState } from 'recoil';
import { memoize } from 'lodash';

import './Editor.css'


// 用 recoil 管理数据，每个 block 分别渲染自己


const atomById = memoize(uuid => atom({
  key: `para-${uuid}`,
  default: {
    type: 'para',
    text: 'new paragraph',
  },
}));

// 代表一个段落级元素，如：标题、正文、表格、图片
const ParaBlock = ({uuid}) => {
  const [state] = useRecoilState(atomById(uuid));
  return (
    <p className="para">{state.text}</p>
  );
};

const Editor = () => {
  return (
    <RecoilRoot>
      <div className="fullscreen">
        <ParaBlock uuid='123' />
        <ParaBlock uuid='456' />
        <p className="para">Hello, world!</p>
        <p className="para">Lorem Ipsum dolor sit amet.</p>
      </div>
    </RecoilRoot>
  );
};

export default Editor;

// JointJS

import { useEffect, useRef, useState } from 'react';

import * as joint from '@joint/core';

const Joint = () => {
  const wrapper = useRef(null);
  const el = useRef(null);

  const [data, _] = useState({
    root: {
      name: '老祖宗',
      mates: [],
      children: [],
    }
  });

  const graph = useRef(null);
  const paper = useRef(null);

  // 初始化
  useEffect(() => {
    // wrapper.current.clientHeight
    graph.current = new joint.dia.Graph({}, { cellNamespace: joint.shapes });
    paper.current = new joint.dia.Paper({
      el: el.current,
      model: graph.current,
      width: wrapper.current.clientWidth,
      height: wrapper.current.clientHeight,
      gridSize: 1,
      cellViewNamespace: joint.shapes,
    });

    // 如果 resize，也要调整 paper 尺寸
    // 无法监听 wrapper 缩放，只能监听整个窗口
    window.addEventListener('resize', () => {
      paper.current.setDimensions(wrapper.current.clientWidth, wrapper.current.clientHeight);
    });

    var rect = new joint.shapes.standard.Rectangle();
    rect.position(100, 30);
    rect.resize(100, 40);
    rect.attr({
      body: {
        fill: 'blue'
      },
      label: {
        text: 'Hello',
        fill: 'white'
      }
    });
    rect.addTo(graph.current);

    var rect2 = rect.clone();
    rect2.translate(300, 0);
    rect2.attr('label/text', 'World!');
    rect2.addTo(graph.current);

    var link = new joint.shapes.standard.Link();
    link.source(rect);
    link.target(rect2);
    link.addTo(graph.current);
  }, []);

  // 更新
  useEffect(() => {
    //
  }, [data]);

  return <div ref={wrapper} style={{
    width: '100%',
    height: '100%',
  }}>
    <div ref={el}/>
  </div>;
};



export default Joint;

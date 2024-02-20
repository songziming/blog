// JointJS

import { useEffect, useRef, useState } from 'react';

import * as joint from '@joint/core';


// 新增祖先节点
var addAncestorTool = new joint.elementTools.Button({
  focusOpacity: 0.5,
  x: '0%',
  y: '50%',
  offset: { x: -5, y: -5 },
  action: function(evt) {
    alert('View id: ' + this.id + '\n' + 'Model id: ' + this.model.id);
  },
  markup: [{
    tagName: 'circle',
    selector: 'button',
    attributes: {
      'r': 7,
      'fill': '#001DFF',
      'cursor': 'pointer'
    }
  }, {
    tagName: 'path',
    selector: 'icon',
    attributes: {
      'd': 'M -2 4 2 4 M 0 3 0 0 M -2 -1 1 -1 M -1 -4 1 -4',
      'fill': 'none',
      'stroke': '#FFFFFF',
      'stroke-width': 2,
      'pointer-events': 'none'
    }
  }]
});

// var boundaryTool = new joint.elementTools.Boundary();
// var removeTool = new joint.elementTools.Remove();
// var toolsView = new joint.dia.ToolsView({
//   tools: [ boundaryTool, removeTool ]
// });




// 每个 element 都要单独创建 tools
const createToolsView = () => {
  var boundaryTool = new joint.elementTools.Boundary();
  var removeTool = new joint.elementTools.Remove();
  var toolsView = new joint.dia.ToolsView({
    tools: [ boundaryTool, removeTool ]
  });
  return toolsView;
}


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
      if (!!wrapper.current) {
        paper.current.setDimensions(wrapper.current.clientWidth, wrapper.current.clientHeight);
      }
    });

    // 注册一些事件处理函数
    paper.current.on('element:pointerdblclick', (elem) => {
      console.log(`double click on element`);
    });
    paper.current.on('element:mouseenter', (elementView) => {
      elementView.showTools();
    });
    paper.current.on('element:mouseleave', (elementView) => {
      elementView.hideTools();
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

    // 添加按钮
    rect.findView(paper.current).addTools(createToolsView());
    rect2.findView(paper.current).addTools(createToolsView());

    // 初始状态，隐藏所有按钮
    paper.current.hideTools();
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

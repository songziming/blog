import { useCallback, useRef, useState, useEffect } from "react";

import { UserOutlined } from '@ant-design/icons';
import { Button, Space, Input, Switch, ConfigProvider } from 'antd';

import ReactFlow, {
    Background,
    Controls,
    applyNodeChanges,
    applyEdgeChanges,
    addEdge,
    Handle,
    Position,
} from 'reactflow';

import DeletableEdge from './FlowEdge';


import 'reactflow/dist/style.css';



// 自定义节点，表示一个人
// 左端口连接父母，右端口连接子女
// 可以直接在节点上编辑姓名、性别、备注信息
const PersonNode = (props) => {

    // 如何在子节点中发送数据更新请求？
    const onChangeGender = useCallback((evt) => {
        console.log(evt.target.value);
    }, []);


    // 姓名输入框和性别按钮不能拖动
    // 必须留出足够的可拖拽面积
    return <>
        <div style={{
            padding: '10px 20px',
            width: '160px', // 根据输入的姓名自动调整宽度？
            backgroundColor: 'white',
            borderRadius: '3px',
            borderWidth: '1px',
            borderStyle: 'solid',
            borderColor: props.selected ? 'red' : '#1a192b',

            boxShadow: props.selected ? '0 0 0 0.5px red' : null,
        }}>
            {/* 用于输入的控件不能干扰拖拽 */}
            <Space align="center">
                <UserOutlined />
                <Input className="nodrag" size="small" variant="borderless" placeholder="name here" />

                {/* switch 显示性别，默认主题色是蓝色，代表男，把disable颜色设为粉色，代表女 */}
                <ConfigProvider theme={{
                    token: {
                        colorTextQuaternary: '#ffa39e',  // switch disabled
                        colorTextTertiary: '#ffccc7',  // switch disabled hover
                    }
                }}>
                    <Switch className="nodrag" checkedChildren="男" unCheckedChildren="女" />
                </ConfigProvider>
            </Space>
        </div>
        <Handle type="target" position={Position.Left} />
        <Handle type="source" position={Position.Right} />
    </>;
};



// node type、edge type 需要定义在组件外部，否则每次渲染都会创建新的 type
const nodeTypes = {
    person: PersonNode
};
const edgeTypes = {
    'deletable-edge': DeletableEdge,
};






// default、input、output 类型的 node 会使用这些属性
const nodeDefaults = {
    sourcePosition: Position.Right,
    targetPosition: Position.Left,
};


const initialNodes = [{
    id: '1',
    data: { label: 'Hello' },
    position: { x: 0, y: 0 },
    type: 'input',
    ...nodeDefaults,
}, {
    id: '2',
    data: { label: 'World' },
    position: { x: 100, y: 100 },
    ...nodeDefaults,
}, {
    id: '3',
    type: 'person',
    position: { x: 0, y: 200 },
    data: { label: '张三', gender: '男' },
    ...nodeDefaults,
}];

// const initialEdges = [{
//     id: '1-2', source: '1', target: '2', label: 'to the', type: 'step'
// }];






const Flow = () => {
    const wrapper = useRef(null);
    // const element = useRef(null);

    const [nodes, setNodes] = useState(initialNodes);
    const [edges, setEdges] = useState([]);

    const onNodesChange = useCallback((changes) => {
        setNodes((nds) => applyNodeChanges(changes, nds));
    }, []);
    const onEdgesChange = useCallback((changes) => {
        setEdges((eds) => applyEdgeChanges(changes, eds));
    }, []);

    // 用户建立节点间连接时调用
    const onConnect = useCallback((params) => {
        // console.log('connecting', params);
        if (params.source == params.target) {
            // console.log('cannot form self loop');
            return;
        }
        const edge = { ...params, type: 'deletable-edge' };
        setEdges((eds) => addEdge(edge, eds));
    }, []);

    return <div ref={wrapper} style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
    }}>
        <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            // fitView
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
        >
            <Background />
            <Controls />
        </ReactFlow>
    </div>
};

export default Flow;

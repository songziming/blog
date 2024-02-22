import { useCallback, useRef, useState, useEffect } from "react";

import { UserOutlined } from '@ant-design/icons';
import { Layout, Flex, Button, Space, Input, Switch, ConfigProvider, Modal, notification } from 'antd';

import ReactFlow, {
    ReactFlowProvider, useReactFlow,
    Background, Controls, MiniMap,
    applyNodeChanges,
    applyEdgeChanges,
    addEdge,
    Handle,
    Position,
} from 'reactflow';

import DeletableEdge from './FlowEdge';


import 'reactflow/dist/style.css';




// 默认主题色是蓝色，代表男，把 disable 颜色设为粉色，代表女
const GenderSwitch = ({gender, onChangeGender}) => {
    return <ConfigProvider theme={{
        token: {
            colorTextQuaternary: '#ffa39e',  // switch disabled
            colorTextTertiary: '#ffccc7',  // switch disabled hover
        }
    }}>
        <Switch className="nodrag" checkedChildren="男" unCheckedChildren="女"
            checked={gender} onChange={onChangeGender} />
    </ConfigProvider>;
};



// 自定义节点，表示一个人
// 左端口连接父母，右端口连接子女
// 可以直接在节点上编辑姓名、性别、备注信息
const PersonNode = ({id, data, selected}) => {
    const flow = useReactFlow();

    const onChangeGender = useCallback((checked) => {
        flow.setNodes((nodes) => nodes.map(
            (node) => ((id === node.id) ? {
                ...node,
                data: { ...node.data, gender: checked },
            }: node)
        ));
    }, []);

    const onRename = useCallback((e) => {
        flow.setNodes((nodes) => nodes.map(
            (node) => ((id === node.id) ? {
                ...node,
                data: { ...node.data, name: e.target.value },
            }: node)
        ));
    }, []);

    // 姓名输入框和性别按钮不能拖动，必须留出足够的可拖拽面积
    return <div style={{
        padding: '5px 10px',
        width: '160px', // 根据输入的姓名自动调整宽度？
        backgroundColor: 'white',
        borderRadius: '3px',
        borderWidth: '1px',
        borderStyle: 'solid',
        borderColor: selected ? 'red' : '#1a192b',
        boxShadow: selected ? '0 0 0 0.5px red' : null,
    }}>
        <Space align="center">
            <UserOutlined />
            <Input className="nodrag" size="small" variant="filled" placeholder="姓名" defaultValue={data.name} onChange={onRename} />
            <GenderSwitch gender={data.gender} onChangeGender={onChangeGender} />
        </Space>
        <Handle type="target" position={Position.Left} />
        <Handle type="source" position={Position.Right} />
    </div>;
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
    type: 'person',
    sourcePosition: Position.Right,
    targetPosition: Position.Left,
};


const edgeOptions = {
    style: {
        stroke: '#333',
    },
    animated: true,
};






const FlowView = () => {
    const [nodes, setNodes] = useState([]);
    const [edges, setEdges] = useState([]);

    const onNodesChange = useCallback((changes) => {
        setNodes((nds) => applyNodeChanges(changes, nds));
    }, []);
    const onEdgesChange = useCallback((changes) => {
        setEdges((eds) => applyEdgeChanges(changes, eds));
    }, []);

    // 用户建立节点间连接时调用
    const onConnect = useCallback((params) => {
        if (params.source === params.target) {
            return;
        }
        const edge = {
            ...params,
            id: `${params.source}-${params.target}`,
            type: 'deletable-edge'
        };
        setEdges((eds) => addEdge(edge, eds));
    }, []);

    return <div style={{ height: '100%' }}>
        <ReactFlow
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            defaultEdgeOptions={edgeOptions}
            fitView
            attributionPosition="bottom-left"
            snapToGrid
            snapGrid={[10,10]}
        >
            <Background />
            <Controls />
            <MiniMap zoomable pannable style={{ height: 120 }} />
        </ReactFlow>
    </div>
};

const FlowApp = () => {
    const [modalOpen, setModalOpen] = useState(false);
    const [api, contextHolder] = notification.useNotification();

    // const box = useRef(null);
    const loadText = useRef('');

    const flow = useReactFlow();

    const nodeId = useRef(0);

    // 我们只关注node、edge 有限的属性
    const onSave = useCallback(() => {
        const nodes = flow.getNodes().map((node) => ({
            id: node.id,
            data: node.data,
            position: node.position,
        }));
        const edges = flow.getEdges().map((edge) => ({
            id: edge.id,
            source: edge.source,
            target: edge.target,
        }));
        let data = {
            nodes,
            edges,
            next: nodeId.current,
        };
        const str = JSON.stringify(data);
        console.log(str);
        navigator.clipboard.writeText(str);
        api.info({
            message: '已保存到剪贴板',
            placement: 'topRight',
        });
    }, []);

    const onLoad = useCallback(() => {
        setModalOpen(true);
    }, [setModalOpen]);

    const handleCancel = useCallback(() => {
        setModalOpen(false);
    }, [setModalOpen]);

    const handleOk = () => {
        setModalOpen(false);
        console.log('parsing', loadText.current);
        let data;
        try {
            data = JSON.parse(loadText.current);
            nodeId.current = data['next'];
            flow.setNodes(
                data['nodes'].map(node => ({ ...node, ...nodeDefaults })
            ));
            flow.setEdges(
                data['edges'].map(edge => ({ ...edge, type: 'deletable-edge' })
            ));
        } catch (e) {
            api.warning({
                message: '格式不正确',
                description: e.message,
                placement: 'topRight',
            });
        }
    };

    const onCreateNode = useCallback(() => {
        flow.addNodes({
            id: `${++nodeId.current}`,
            position: { x: 50, y: 50 },
            data: { name: '张三', gender: true },
            ...nodeDefaults,
        });
    }, []);

    // const notify = (msg) => {
    //     api.info({
    //         message: msg,
    //         placement: 'topRight',
    //     })
    // };

    return <Layout style={{ height: '100%' }}>
        {contextHolder}
        <Modal title='粘贴在这里' open={modalOpen} onOk={handleOk} onCancel={handleCancel}>
            <Input.TextArea rows={6} onChange={(e) => {
                loadText.current = e.target.value;
            }} />
        </Modal>
        <Layout.Header style={{ display: 'flex', alignItems: 'center' }}>
            <Flex gap="small" wrap="wrap">
                <Button onClick={onSave}>保存</Button>
                <Button onClick={onLoad}>打开</Button>
                <Button onClick={onCreateNode}>新建节点</Button>
            </Flex>
        </Layout.Header>
        <Layout.Content>
            <FlowView/>
        </Layout.Content>
    </Layout>;
};


export default () => <ReactFlowProvider>
    <FlowApp />
</ReactFlowProvider>;

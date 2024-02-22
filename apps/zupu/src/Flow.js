import { useCallback, useRef, useState } from "react";

import { Layout, Flex, Button, Input, Modal, notification } from 'antd';

import ReactFlow, {
    // ReactFlowProvider, useReactFlow,
    Background, Controls, MiniMap,
    useNodesState, useEdgesState,
    Position,
    addEdge, getConnectedEdges, getNodesBounds, getViewportForBounds,
} from 'reactflow';

import { toPng } from 'html-to-image';

import PersonNode from './FlowNode';
import DeletableEdge from './FlowEdge';


import 'reactflow/dist/style.css';






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




const downloadImage = (dataUrl) => {
    const a = document.createElement('a');

    a.setAttribute('download', 'reactflow.png');
    a.setAttribute('href', dataUrl);
    a.click();
};




const FlowApp = () => {
    const [modalOpen, setModalOpen] = useState(false);
    const [api, contextHolder] = notification.useNotification();

    const maxId = useRef(0);
    const loadText = useRef('');

    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);


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
    }, [setEdges]);

    const onCreateNode = useCallback(() => {
        setNodes(nds => nds.concat({
            id: `${++maxId.current}`,
            position: { x: 50, y: 50 },
            data: { name: '张三', gender: true },
            ...nodeDefaults,
        }));
    }, [setNodes]);

    const onRemoveNode = useCallback(() => {
        const selNodes = nodes.filter(node => node.selected);
        const selEdges = getConnectedEdges(selNodes, edges);
        setEdges(edges.filter(e => !selEdges.includes(e)));
        setNodes(nodes.filter(v => !v.selected));
    }, [nodes, edges, setNodes, setEdges]);

    // 我们只关注node、edge 有限的属性
    const onSave = useCallback(() => {
        let data = {
            nodes: nodes.map(node => ({
                id: node.id,
                data: node.data,
                position: node.position,
            })),
            edges: edges.map(edge => ({
                id: edge.id,
                source: edge.source,
                target: edge.target,
            })),
            maxId: maxId.current,
        };
        const str = JSON.stringify(data);
        console.log(str);
        navigator.clipboard.writeText(str);
        api.info({
            message: '已保存到剪贴板',
            placement: 'topRight',
        });
    }, [api, nodes, edges]);

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
            maxId.current = data['maxId'];
            setNodes(
                data['nodes'].map(node => ({ ...node, ...nodeDefaults })
            ));
            setEdges(
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

    // 导出 png 并下载（提高分辨率）
    const onExport = useCallback(() => {
        const bounds = getNodesBounds(nodes);
        const im_width = bounds.width * 4;
        const im_height = bounds.height * 4;
        console.log(bounds);
        const transform = getViewportForBounds(bounds, im_width, im_height, 0.5, 8);

        toPng(document.querySelector('.react-flow__viewport'), {
            backgroundColor: '#fff',
            width: im_width,
            height: im_height,
            style: {
                width: im_width,
                height: im_height,
                transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.zoom})`,
            },
        }).then(downloadImage);
    }, [nodes]);


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
                <Button onClick={onCreateNode}>新建</Button>
                <Button onClick={onRemoveNode}>删除</Button>
                <Button onClick={onExport}>导出</Button>
            </Flex>
        </Layout.Header>
        <Layout.Content>
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
                <Background gap={10} />
                <Controls />
                <MiniMap zoomable pannable style={{ height: 120 }} />
            </ReactFlow>
        </Layout.Content>
    </Layout>;
};


export default FlowApp;

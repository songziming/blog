import { useCallback } from "react";

import { UserOutlined } from '@ant-design/icons';
import { Space, Input, Switch, ConfigProvider } from 'antd';

import {
    useReactFlow, Handle, Position,
} from 'reactflow';

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
    }, [flow, id]);

    const onRename = useCallback((e) => {
        flow.setNodes((nodes) => nodes.map(
            (node) => ((id === node.id) ? {
                ...node,
                data: { ...node.data, name: e.target.value },
            }: node)
        ));
    }, [flow, id]);

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

export default PersonNode;

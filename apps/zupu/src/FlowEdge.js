// 适用于 ReactFlow 的自定义边
// 带有一个删除按钮，只有hover或选中时才显示

import {
    BaseEdge,
    EdgeLabelRenderer,
    getSimpleBezierPath,
    Position,
    useReactFlow,
} from 'reactflow';

const DeletableEdge = ({ id, sourceX, sourceY, targetX, targetY, selected }) => {
    const { setEdges } = useReactFlow();

    const [edgePath, labelX, labelY] = getSimpleBezierPath({
        sourceX, sourceY, sourcePosition: Position.Right,
        targetX, targetY, targetPosition: Position.Left,
    });

    return <>
        <BaseEdge id={id} path={edgePath} />
        {selected && <EdgeLabelRenderer>
            <button className="nodrag nopan" style={{
                    position: 'absolute',
                    transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
                    pointerEvents: 'all',
                }}
                onClick={() => {
                    setEdges((es) => es.filter((e) => e.id !== id));
                }}
            >X</button>
        </EdgeLabelRenderer> }
    </>;
};

export default DeletableEdge
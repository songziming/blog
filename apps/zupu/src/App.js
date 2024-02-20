import './App.css';


import Joint from './Joint';

// import { ConfigProvider, theme } from 'antd';

// import { Space, Button } from 'antd';

// import { Breadcrumb, Layout, Menu } from 'antd';
// const { Header, Content, Sider } = Layout;

// function App() {
//   return (
//     <div className="App">
//       <header className="App-header">
//         <p>spans the complete page.</p>
//         <p>
//           Edit <code>src/App.js</code> and save to reload.
//         </p>
//         <a
//           className="App-link"
//           href="https://reactjs.org"
//           target="_blank"
//           rel="noopener noreferrer"
//         >
//           Learn React
//         </a>
//       </header>
//     </div>
//   );
// }


// const MainWindow = () => (
//   <Space>
//     <Button type="primary">Open</Button>
//     <Button>Default</Button>
//   </Space>
// );


// const items1 = [1,2,3,4].map((v) => ({
//   key: `${v}`,
//   label: `nav ${v}`,
// }));


// const AntDesignApp = () => (
//   <ConfigProvider theme={{
//     algorithm: [theme.darkAlgorithm, theme.compactAlgorithm],
//   }}>
//     <Layout>
//       <Header style={{ display: 'flex', alignItems: 'left'}}>
//         <Menu
//           mode="horizontal"
//           defaultSelectedKeys={['2']}
//           items={items1}
//           style={{
//             flex: 1,
//             minWidth: 0,
//           }}
//         />
//       </Header>
//       {/* <MainWindow/> */}
//       <Joint/>
//     </Layout>
//   </ConfigProvider>
// );

const App = () => <Joint/>;

export default App;

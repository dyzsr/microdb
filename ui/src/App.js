import React, {useState, useRef} from 'react';
//import { render } from 'react-dom';

import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
//import Icon from '@material-ui/core/Icon';
import FolderOpenIcon from '@material-ui/icons/FolderOpen';
import SaveAltIcon from '@material-ui/icons/SaveAlt';
import PlayCircleFilledIcon from '@material-ui/icons/PlayCircleFilled';
import ExitToAppIcon from '@material-ui/icons/ExitToApp';

import Table from '@material-ui/core/Table';
import TableHead from '@material-ui/core/TableHead';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableRow from '@material-ui/core/TableRow';

//import brace from 'brace';
import AceEditor from 'react-ace';

//import Dimensions from 'react-dimensions';
import ContainerDimensions from 'react-container-dimensions';

import { makeStyles } from '@material-ui/styles';

import 'brace/mode/mysql';
import 'brace/theme/github';


const process = require('process');

var fileDownload = require('js-file-download');

var storage = window.localStorage;


const useStyles = makeStyles({
	root: {
		display: 'flex',
		width: '100%',
		height: '100%',
		alignItems: 'stretch',
	},

	appBar: {
		display: 'flex',
		height: '7%',
		justifyContent: 'center',
		background: '#3388ee',
	},

	toolbar: {
		width: '100%',
	},

	toolbarLeft: {
		flex: 1,
		justifyContent: 'flex-start',
	},

	toolbarRight: {
		flex: 1,
		justifyContent: 'flex-end',
	},

	content: {
		justifyContent: 'flex-start',
		display: 'flex',
		flexGrow: 1,
		paddingTop: '6%',
		paddingBottom: '5%',
		background: '#334455',
	},

	editorpane: {
		display: 'block',
		flex: 1,
		marginLeft: '20px',
		marginRight: '8px',
		marginBottom: '20px',
		background: '#559999',
	},

	resultpane: {
		display: 'block',
		flex: 1,
		marginLeft: '8px',
		marginRight: '20px',
		marginBottom: '20px',
		background: '#bb8877',
	},

	resultbody: {
		background: '#ffffff',
	},

	resultblock: {
		marginLeft: '10px',
		marginRight: '10px',
		borderBottomStyle: 'solid',
		borderBottomWidth: '1px',
	},

	result: {
		background: '#ffffff',
		marginLeft: '10px',
		marginRight: '10px',
	},

	blockHead: {
		//height: '7%',
	},

	blockBody: {
		background: '#ffffff',
		height: '95%',
	},

	blockTitle: {
		marginLeft: '10px',
	},

	h3: {
		paddingTop: '10px',
		//paddingBottom: '5px',
	},

	tablename: {
		marginLeft: '10px',
		marginRight: '20px',
		color: '#5577bb',
	},

	info: {
		marginLeft: '10px',
		marginRight: '20px',
		color: '#5577bb',
	},

	error: {
		marginLeft: '10px',
		marginRight: '20px',
		color: '#ee2200',
	},
});

// Multiple table results may be presented

const TableResult = ({name, meta, values, id}) => {
	const classes = useStyles();

	return (
		<div className={classes.result} key={`res_${id}`}>
			<h3 className={classes.h3}>
				查询结果
			</h3>

			<p className={classes.tablename}>
				{name}
			</p>

			<Table>
				<TableHead>
					<TableRow>
						{
							meta.map((cell, id2) => (
								<TableCell key={`res_${id}_meta_${id2}`}>
									{cell}
								</TableCell>
							))
						}
					</TableRow>
				</TableHead>

				<TableBody>
					{
						values.map((row, id3) => (
							<TableRow key={`res_${id}_row_${id3}`}>
								{
									row.map((cell, id4) => (
										<TableCell key={`res_${id}_row_${id3}_col_${id4}`}>
											{''+cell}
										</TableCell>
									))
								}
							</TableRow>
						))
					}
				</TableBody>
			</Table>
		</div>
	);
}

const InfoResult = ({info, id}) => {
	const classes = useStyles();
	
	return (
		<div className={classes.result} key={`res_${id}`}>
			<h3 className={classes.h3}>
				执行信息
			</h3>
			<p className={classes.info}>{info}</p>
		</div>
	);
}

const ErrorResult = ({info, id}) => {
	const classes = useStyles();
	
	return (
		<div className={classes.result} key={`res_${id}`}>
			<h3 className={classes.h3}>
				错误信息
			</h3>
			<p className={classes.error}>{info}</p>
		</div>
	);
}

const ResultView = ({tables}) => {
	const classes = useStyles();

	return (
		<div>
			{
				tables.map((result, id) => (
					<div className={classes.resultblock}>
						{
							((result) => {
								if (result.type === 'table') {
									return (
										<TableResult
											name={result.name}
											meta={result.meta}
											values={result.values}
											id={id}
										/>
									);
								} else if (result.type === 'info') {
									return <InfoResult info={result.info} id={id} />;
								} else {
									return <ErrorResult info={result.info} id={id} />;
								}
							}) (result)
						}
					</div>
				))
			}
		</div>
	);
}

const App = (props) => {
	const classes = useStyles();

	// source code in SQL
	let init_code = storage.getItem('code');
	if (init_code == null)
		init_code = '';
	const [code, setCode] = useState(init_code);

	const onChangeCode = (code) => {
		storage.setItem('code', code);
		setCode(code);
	};

	// table results
	let init_tables = storage.getItem('tables');
	if (init_tables == null)
		init_tables = [];
	else
		init_tables = JSON.parse(init_tables);
	const [tables, setTables] = useState(init_tables);

	// load the code from files
	const openFile = useRef(null);
	const onOpenFile = (files) => {
		console.log(files);
		if (files.length > 0) {
			const file = files[0];

			var reader = new FileReader();
			reader.onload = () => {
				const data = reader.result;
				console.log(data);
				setCode(data);
				storage.setItem('code', data);
			};

			reader.readAsText(file);
		} else {
			alert('Failed to load file');
		}
	};

	const onSaveAs = () => {
		fileDownload(code, 'query.sql');
	};

	// run the code
	const onPlay = () => {
		fetch('http://localhost:30000', {
			method: 'POST',
			mode: 'cors',
			cache: 'no-cache',
			credentials: 'same-origin',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				'data': code,
			}),
		})
			.then(response => response.json())
			.then(json => {
				const results = json['results'];
				setTables(results);
				console.log(results);

				storage.setItem('tables', JSON.stringify(results));
			})
			.catch(err => alert(err));
		console.log(code);
	};

	const onExit = () => {
		fetch('http://localhost:30000/exit', {
			method: 'GET',
			mode: 'cors',
			cache: 'no-cache',
			credentials: 'same-origin',
		})
			.then(response => response.text())
			.then(text => {
				alert('退出数据库');
			})
			.catch(error => alert(error));
	};

	return (
		<div className={classes.root}>
			<AppBar className={classes.appBar}>
				<Toolbar className={classes.toolbar}>
					<div className={classes.toolbarLeft}>
						{/* Open file button */}
						<IconButton onClick={() => openFile.current.click()}>
							<FolderOpenIcon />
							<input
								type="file"
								ref={openFile}
								onChange={event => onOpenFile(event.target.files)} 
								style={{display: 'none'}}
								accept=".sql,.txt"
							/>
						</IconButton>

						{/* Save As button */}
						<IconButton onClick={() => onSaveAs()}>
							<SaveAltIcon />
						</IconButton>
					</div>

					<div className={classes.toolbarRight}>
						{/* Run code button */}
						<IconButton onClick={() => onPlay()}>
							<PlayCircleFilledIcon />
						</IconButton>

						{/* Exit button */}
						<IconButton onClick={() => onExit()}>
							<ExitToAppIcon />
						</IconButton>
					</div>
				</Toolbar>
			</AppBar>

			<main className={classes.content}>
				{/* Editor Window */}
				<div className={classes.editorpane}>
					<div className={classes.blockHead}>
						<h2 className={classes.blockTitle}>
							编辑查询
						</h2>
					</div>

					<div className={classes.blockBody}>
						<ContainerDimensions>
							{({width, height}) => (
								<AceEditor
									mode="mysql"
									theme="github"
									onChange={(code) => onChangeCode(code)}
									value={code}
									width={`${width - 1}px`}
									height={`${height - 1}px`}
								/>
							)}
						</ContainerDimensions>
					</div>
				</div>

				{/* Results Window */}
				<div className={classes.resultpane}>
					<div className={classes.blockHead}>
						<h2 className={classes.blockTitle}>
							查询结果
						</h2>
					</div>

					<div className={classes.blockBody}>
						<ResultView tables={tables} />
					</div>
				</div>
			</main>
		</div>
	);
}

export default App;

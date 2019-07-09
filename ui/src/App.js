import React, {useState, useRef} from 'react';
//import { render } from 'react-dom';

import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
//import Icon from '@material-ui/core/Icon';
import FolderOpenIcon from '@material-ui/icons/FolderOpen';
import SaveIcon from '@material-ui/icons/Save';
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


var storage = window.localStorage;


const useStyles = makeStyles({
	root: {
		display: 'flex',
	},

	appBar: {
		display: 'flex',
		height: '50px',
		justifyContent: 'center',
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
		paddingTop: '50px',
		//paddingLeft: '20px',
		height: '100%',
	},

	editor: {
		flex: 1,
		justifyContent: 'center',
		alignItems: 'center',
		borderWidth: '1px',
		borderStyle: 'solid',
		//width: '50%',
		marginLeft: '5px',
		marginRight: '2px',
		marginTop: '2px',
	},

	result: {
		flex: 1,
		//width: '50%',
		borderWidth: '1px',
		borderStyle: 'solid',
		marginLeft: '2px',
		marginRight: '5px',
		marginTop: '2px',
	},

	table: {
		borderBottomStyle: 'solid',
		borderBottomWidth: '1px',
	},

	blockTitle: {
		marginLeft: '10px',
	},
});

// Multiple table results may be presented

const TableResult = ({tables}) => {
	const classes = useStyles();

	return (
		<div> {
			tables.map(({meta, values}, id1) => (
				<div className={classes.table} key={`table_${id1}`}>
					<Table>
						<TableHead>
							<TableRow>
									{
										meta.map((cell, id2) => (
											<TableCell key={`table_${id1}_meta_${id2}`}>
													{cell}
											</TableCell>
										))
									}
							</TableRow>
						</TableHead>

						<TableBody>
								{
									values.map((row, id3) => (
										<TableRow key={`table_${id1}_row_${id3}`}>
												{
													row.map((cell, id4) => (
														<TableCell key={`table_${id1}_row_${id3}_col_${id4}`}>
																{cell}
														</TableCell>
													))
												}
										</TableRow>
									))
								}
						</TableBody>
					</Table>
				</div>
			))
		} </div>
	);
}

const App = (props) => {
	const classes = useStyles();

	let init_code = storage.getItem('code');
	if (init_code == null)
		init_code = '';
	// source code in SQL
	const [code, setCode] = useState(init_code);

	const onChangeCode = (code) => {
		storage.setItem('code', code);
		setCode(code);
	};

	let init_tables = storage.getItem('tables');
	if (init_tables == null)
		init_tables = [];
	else
		init_tables = JSON.parse(init_tables);
	// table results
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

	// save the code into files
	const saveFile = useRef(null);
	const onSave = () => {
	};

	const onSaveAs = () => {
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
			});
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
				alert('exited.' + text);
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
						
							{/* Save file button */}
						<IconButton onClick={() => onSave()}>
							<SaveIcon />
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
				<div className={classes.editor}>
					<h2 className={classes.blockTitle}>
						编辑查询
					</h2>
					<ContainerDimensions>
							{({width, height}) => (
								<AceEditor
									mode="mysql"
									theme="github"
									onChange={(code) => onChangeCode(code)}
									value={code}
									width={`${width - 10}px`}
									//height={`500px`}
									//width={`${width}px`}
									//height={`{height}px`}
								/>
							)}
					</ContainerDimensions>
				</div>

					{/* Results Window */}
				<div className={classes.result}>
					<h2 className={classes.blockTitle}>
							查询结果
					</h2>

					<TableResult tables={tables} />
				</div>
			</main>
		</div>
	);
}

export default App;

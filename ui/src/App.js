import React, {useState, useRef} from 'react';
//import { render } from 'react-dom';

import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import IconButton from '@material-ui/core/IconButton';
//import Icon from '@material-ui/core/Icon';
import FolderOpenIcon from '@material-ui/icons/FolderOpen';
import SaveIcon from '@material-ui/icons/Save';
import PlayCircleFilledIcon from '@material-ui/icons/PlayCircleFilled';

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

const TableResult = ({tables}) => {
	const classes = useStyles();

	return (
		<div> {
			tables.map(({meta, values}, id1) => (
				<div className={classes.table} key={'table_' + id1}>
					<Table>
						<TableHead>
							<TableRow>
									{
										meta.map((cell, id2) => (
											<TableCell key={'table_' + id1 + '_meta_' + id2}>
													{cell}
											</TableCell>
										))
									}
							</TableRow>
						</TableHead>

						<TableBody>
								{
									values.map((row, id3) => (
										<TableRow key={'table_' + id1 + '_row_' + id3}>
												{
													row.map((cell, id4) => (
														<TableCell key={'table_'+id1+'_row_'+id3+'_col_'+id4}>
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

	const [code, setCode] = useState('');

	const [tables, setTables] = useState([]);

	const openFile = useRef(null);
	const onOpenFile = (event) => {
		
	};

	const onSave = () => {
	};

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
			});
		console.log(code);
	}

	return (
		<div className={classes.root}>
			<AppBar className={classes.appBar}>
				<Toolbar className={classes.toolbar}>
					<div className={classes.toolbarLeft}>
						<IconButton onClick={() => openFile.current.click()}>
							<FolderOpenIcon />
							<input
								type="file"
								ref={openFile}
								onChange={event => onOpenFile(event)} 
								style={{display: 'none'}}
							/>
						</IconButton>
						<IconButton>
							<SaveIcon />
						</IconButton>
					</div>

					<div className={classes.toolbarRight}>
						<IconButton onClick={() => onPlay()}>
							<PlayCircleFilledIcon />
						</IconButton>
					</div>
				</Toolbar>
			</AppBar>

			<main className={classes.content}>
				<div className={classes.editor}>
					<h2 className={classes.blockTitle}>
						编辑查询
					</h2>
					<ContainerDimensions>
							{({width, height}) => (
								<AceEditor
									mode="mysql"
									theme="github"
									onChange={(code) => setCode(code)}
									value={code}
									width={width - 10}
									height={500}
								/>
							)}
					</ContainerDimensions>
				</div>

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

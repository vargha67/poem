const express = require("express")
const spawn = require("child_process").spawn
const path = require('path')
const router = express.Router()


function loadPatterns(dataset, model, ruleMethods, expMinSupport, idsMinSupport, cartMinSamplesLeaf) {
	return new Promise((resolve, reject) => {
		if (!dataset || !model || !ruleMethods || (ruleMethods.length == 0)) {
			return reject(new Error('Either the dataset, the CNN model, or the rule method(s) is not specified!'))
		}
		
		const ruleMethodsStr = ruleMethods.join(',')
		const pythonProcess = spawn('env/bin/python', ["src/server/data_processing.py", "load_patterns", dataset, model, ruleMethodsStr, expMinSupport, idsMinSupport, cartMinSamplesLeaf])
		
		pythonProcess.stdout.on('data', (data) => {
			//console.log('Server - stdout result:', data.toString())
			return resolve(data.toString())
		})
		
		pythonProcess.stderr.on('data', (data) => {
			console.log('Server - stderr result:', data.toString())
			return reject(new Error('An error occurred while loading the patterns!'))
		})
	})
}


function loadImagesInfo(dataset, model, ruleMethods, expMinSupport, idsMinSupport, cartMinSamplesLeaf, patternIndex, mode, targetConcept) {
	return new Promise((resolve, reject) => {
		if (!dataset || !model || !ruleMethods || (ruleMethods.length == 0) || !patternIndex || !mode) {
			return reject(new Error('Either the dataset, the CNN model, the rule method(s), or the pattern is not specified!'))
		}
		
		const ruleMethodsStr = ruleMethods.join(',')
		args = ["src/server/data_processing.py", "load_images_info", dataset, model, ruleMethodsStr, expMinSupport, idsMinSupport, cartMinSamplesLeaf, patternIndex, mode]
		if (targetConcept)
			args.push(targetConcept)
			
		const pythonProcess = spawn('env/bin/python', args)
		
		pythonProcess.stdout.on('data', (data) => {
			//console.log('Server - stdout result:', data.toString())
			return resolve(data.toString())
		})
		
		pythonProcess.stderr.on('data', (data) => {
			console.log('Server - stderr result:', data.toString())
			return reject(new Error('An error occurred while loading images info!'))
		})
	})
}


router.get("/patterns", async (req, res) => {
	const dataset = req.query.dataset
	const model = req.query.model
	let ruleMethods = req.query.ruleMethods || []
	if (!Array.isArray(ruleMethods))
		ruleMethods = [ruleMethods]
	const expMinSupport = req.query.expMinSupport || -1
	const idsMinSupport = req.query.idsMinSupport || -1
	const cartMinSamplesLeaf = req.query.cartMinSamplesLeaf || -1
	console.log(`Server - loading patterns for dataset ${dataset}, model ${model}, rule methods ${ruleMethods}, exp min support ${expMinSupport}, 
		ids min support ${idsMinSupport}, cart min samples leaf ${cartMinSamplesLeaf}`)
	
	try {
		const result = await loadPatterns(dataset, model, ruleMethods, expMinSupport, idsMinSupport, cartMinSamplesLeaf)
		//console.log('Server - result patterns:', result)
		return res.send(result)
	}
	catch(err) {
		return res.status(400).send(err.message)
	}
	
	// This code works the same as the code above for getting the result of a function that returns a promise: 
	/*loadPatterns(dataset, model, ruleMethods).then((result) => {
		return res.json(result)
	}, (err) => {
		return res.status(400).send(err.message)
	})*/
})


router.get("/imagesinfo/:patternIndex", async (req, res) => {
	const patternIndex = req.params.patternIndex
	const dataset = req.query.dataset
	const model = req.query.model
	let ruleMethods = req.query.ruleMethods || []
	if (!Array.isArray(ruleMethods))
		ruleMethods = [ruleMethods]
	const mode = req.query.mode
	const targetConcept = req.query.targetConcept
	const expMinSupport = req.query.expMinSupport || -1
	const idsMinSupport = req.query.idsMinSupport || -1
	const cartMinSamplesLeaf = req.query.cartMinSamplesLeaf || -1
	
	console.log(`Server - loading images info for dataset ${dataset}, model ${model}, rule methods ${ruleMethods}, exp min support ${expMinSupport}, 
		ids min support ${idsMinSupport}, cart min samples leaf ${cartMinSamplesLeaf}, pattern index ${patternIndex}, mode ${mode}, and target concept ${targetConcept}`)
	
	try {
		const result = await loadImagesInfo(dataset, model, ruleMethods, expMinSupport, idsMinSupport, cartMinSamplesLeaf, patternIndex, mode, targetConcept)
		//console.log('Server - result images info:', result)
		return res.send(result)
	}
	catch(err) {
		return res.status(400).send(err.message)
	}
})


router.get("/image/*", async (req, res) => {
	const imgPath = req.params[0]
	//console.log(`Server - loading image with path ${imgPath}`)
	let fullPath = path.join(__dirname, imgPath)
	let serverSubPath = path.join('', 'src', 'server')   // '/src/server'
	i = __dirname.lastIndexOf(serverSubPath)
	if (i != -1)
		fullPath = path.join(__dirname.substring(0,i), imgPath)
		
	res.sendFile(fullPath)
})


router.use((_, res) => {
  return res.sendStatus(501)
})


module.exports = router

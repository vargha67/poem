<template>
	<div id="app">
		<div id="header">
			<b-card-text><h4>POEM: Pattern-Oriented Explanations of CNN Models</h4></b-card-text>
		</div>
		
		<b-overlay id="views_container" :show="loading">
			<div id="settings_container">
				<SettingsView />
			</div>
			
			<div id="main_container">
				<div id="patterns_container">
					<PatternsView />
				</div>
				
				<div id="images_container">
					<ImagesView />
				</div>
			</div>
		</b-overlay>
	</div>
</template>


<script>
import axios from "axios";
import SettingsView from "./components/SettingsView.vue";
import PatternsView from "./components/PatternsView.vue";
import ImagesView from "./components/ImagesView.vue";
import EventBus from "./EventBus";
import Events from "./Events";

let dataset = null
let model = null
let ruleMethods = null
let ruleMethodParams = null
let patternIndex = null
let mode = null
let targetConcept = null
let activatedConcepts = null

export default {
	name: 'App',
	components: {
		SettingsView,
		PatternsView,
		ImagesView
	},
	data () {
		return {
			loading: false
		}
	}, 
	methods: {
		startProcess: function(_dataset, _model, _ruleMethods, _ruleMethodParams) {
			if (!_dataset || !_model || !_ruleMethods || (_ruleMethods.length == 0)) {
				this.showErrorMessage('You should select a dataset, a CNN model, and at least one pattern mining method!')
				return
			}
		
			dataset = _dataset
			model = _model
			ruleMethods = _ruleMethods
			ruleMethodParams = _ruleMethodParams
		
			console.log(`Loading patterns from server for dataset ${dataset}, model ${model}, rule methods ${ruleMethods}, and rule method params ${ruleMethodParams} ...`)
			this.loading = true
			const paramsArray = [
		        ["dataset", dataset],
		        ["model", model],
		        ["ruleMethods", ruleMethods]
		    ]
		    
		    ruleMethodParams.forEach((item) => {
		    	paramsArray.push([item.key, item.value])
		    })
		    
		    const params = new URLSearchParams(paramsArray)
		    //const patterns = await axios.get("/api/patterns", { params }).then((res) => res.data)
		    axios.get("/api/patterns", { params }).then((result) => {
		    	setTimeout(() => {   // timeout for a small delay
		    		this.loading = false
					const patterns = result.data || []
					//console.log(patterns)
					EventBus.$emit(Events.DISPLAY_PATTERNS, patterns)
					EventBus.$emit(Events.CLEAR_IMAGES)
		    	}, 1000)
		    	
		    }, (err) => {
		    	this.loading = false
		    	const message = (err.response || {}).data ? err.response.data : 'An error occurred while computing the patterns!'
		    	this.showErrorMessage(message)
		    })
		    
		},
		loadImagesInfo: function(_patternIndex, _mode, _activatedConcepts) {
			patternIndex = _patternIndex
			mode = _mode
			activatedConcepts = _activatedConcepts
				
			console.log(`Loading images info from server for pattern ${patternIndex} and mode ${mode} ...`)
			this.loading = true
			const paramsArray = [
		        ["dataset", dataset],
		        ["model", model],
		        ["ruleMethods", ruleMethods],
		        ["mode", mode]
		    ]
		    
		    ruleMethodParams.forEach((item) => {
		    	paramsArray.push([item.key, item.value])
		    })
		    
		    const params = new URLSearchParams(paramsArray)
		    //const imagesInfo = await axios.get("/api/imagesinfo/" + patternIndex, { params }).then((res) => res.data)
		    axios.get("/api/imagesinfo/" + patternIndex, { params }).then((result) => {
		    	this.loading = false
		    	const imagesInfo = result.data || []
		    	//console.log(imagesInfo)
		    	EventBus.$emit(Events.DISPLAY_IMAGES, imagesInfo, null, patternIndex, mode, activatedConcepts)
		    
		    }, (err) => {
		    	this.loading = false
		    	const message = (err.response || {}).data ? err.response.data : 'An error occurred while loading the images!'
		    	this.showErrorMessage(message)
		    })
		},
		loadImagesInfoForConcept: function(_targetConcept) {
			targetConcept = _targetConcept
				
			console.log(`Loading images info for concept ${targetConcept} from server for pattern ${patternIndex} and mode ${mode} ...`)
			this.loading = true
			const paramsArray = [
		        ["dataset", dataset],
		        ["model", model],
		        ["ruleMethods", ruleMethods],
		        ["mode", mode]
		    ]
		    
		    ruleMethodParams.forEach((item) => {
		    	paramsArray.push([item.key, item.value])
		    })
		    
		    if (targetConcept)
		    	paramsArray.push(["targetConcept", targetConcept])
		    
		    const params = new URLSearchParams(paramsArray)
		    //const imagesInfo = await axios.get("/api/imagesinfo/" + patternIndex, { params }).then((res) => res.data)
		    axios.get("/api/imagesinfo/" + patternIndex, { params }).then((result) => {
		    	this.loading = false
		    	const imagesInfo = result.data || []
		    	//console.log(imagesInfo)
		    	EventBus.$emit(Events.DISPLAY_IMAGES, imagesInfo, targetConcept)
		    
		    }, (err) => {
		    	this.loading = false
		    	const message = (err.response || {}).data ? err.response.data : 'An error occurred while loading the images!'
		    	this.showErrorMessage(message)
		    })
		}, 
		showErrorMessage: function(message) {
			this.$bvToast.toast(message, {
				title: 'Error',
				variant: 'warning',
				toaster: 'b-toaster-top-center'
			})
		}
	},
	mounted: function() {
		EventBus.$on(Events.START_PROCESS, this.startProcess);
		EventBus.$on(Events.LOAD_IMAGES_INFO, this.loadImagesInfo);
		EventBus.$on(Events.LOAD_IMAGES_INFO_FOR_CONCEPT, this.loadImagesInfoForConcept);
	}
}
</script>


<style lang="scss">
html, body {
	height: 100%;
}

#app {
	display: flex;
	flex-direction: column;
	width: 100%;
	height: 100%;
}

#header {
	/*flex: 3%;*/
	width: 100%;
	height: 8%;
	padding: 20px;
}

#views_container {
	/*flex: 97%;*/
	display: flex;
	flex-direction: row;
	width: 100%;
	height: 92%;
	border: 2px solid #999;
}

#settings_container {
	/*flex: 20%;*/
	height: 100%;
	border: 2px solid #999;
	width: 22%;
}

#main_container {
	display: flex;
	flex-direction: column;
	/*flex: 80%;*/
	height: 100%;
	width: 78%;
}

#patterns_container {
	flex: 50%;
	max-height: 50%;
	overflow-y: hidden;
	width: 100%;
	border: 2px solid #999;
}

#images_container {
	flex: 50%;
	max-height: 50%;
	overflow-y: hidden;
	width: 100%;
	border: 2px solid #999;
}

.toast:not(.show) {
   display: block;
}

.b-table-row-selected {
	/*border: 3px solid blue !important;*/
	background-color: #e8e8e8;
}


/* The layout where the settings view is on top and the patterns and images views are in the bottom near each other: 
#app {
	display: flex;
	flex-direction: column;
	width: 100%;
	height: 100%;
}

#header {
	width: 100%;
	padding: 20px;
}

#settings_container {
	width: 100%;
}

#main_container {
	display: flex;
	flex-direction: row;
	width: 100%;
}

#patterns_container {
	flex: 50%;
}

#images_container {
	flex: 50%;
}
*/
</style>

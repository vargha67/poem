<template>
	<div id="images_main">
		<div id="images_empty" v-if="!patternIndex">
			<b-card-text><h5>Select a pattern above and click on one of the options to view the related images</h5></b-card-text>
		</div>
	
		<div id="concepts_chooser" v-if="patternIndex">
			<b-card-body>
				<b-card-text>Choose a concept to see its activation images:</b-card-text>
				<b-form-radio-group v-model="selectedConcept" :options="conceptOptions" stacked></b-form-radio-group>
			</b-card-body>
			
			<b-card-body style="text-align: center;">
				<b-button v-on:click="loadPatternImagesOfConcept()">Show Activation Images</b-button>
			</b-card-body>
			
			<div style="flex-grow: 20;">&nbsp;</div>
		</div>
		
		<div id="images_main_container" v-if="patternIndex">
			<b-card-body id="image_set_desc">
				<b-card-text style="text-align: center;"><h6 style="margin-bottom: 0px;">{{imageSetDesc}}</h6></b-card-text>
			</b-card-body>
		
			<div id="images_gallery">
				<b-card class="image_card" v-for="image in imagesInfo" :img-src="`/api/image/${image.path}`" :key="image.path" img-top>
					<b-card-text class="small" v-html="image.desc"></b-card-text>
				</b-card>
			</div>
		</div>
	</div>
</template>


<script>
import EventBus from "../EventBus"
import Events from "../Events"

export default {
	name: 'ImagesView',
	data () {
		return {
			patternIndex: null,
			mode: null,
			conceptOptions: [],
			imagesInfo: [],
			selectedConcept: null,
			targetConcept: null
		}
	}, 
	methods: {
		displayImages: function(imagesInfo, targetConcept, patternIndex, mode, activatedConcepts) {
			this.imagesInfo = imagesInfo
			this.targetConcept = targetConcept
			this.selectedConcept = targetConcept
			
			if (patternIndex)
				this.patternIndex = patternIndex
			
			if (mode)
				this.mode = mode
				
			if (activatedConcepts) {
				let conceptOptions = []
				activatedConcepts.forEach((c) => {
					conceptOptions.push({text: c, value: c})
				})
				conceptOptions.push({text: 'None', value: null})
				this.conceptOptions = conceptOptions
				//console.log('conceptOptions:', this.conceptOptions)
			}
		}, 
		clearImages: function() {
			this.patternIndex = null
			this.mode = null
			this.conceptOptions = []
			this.imagesInfo = []
			this.selectedConcept = null
			this.targetConcept = null
		},
		loadPatternImagesOfConcept: function() {
			EventBus.$emit(Events.LOAD_IMAGES_INFO_FOR_CONCEPT, this.selectedConcept)
		}
	}, 
	computed: {
		imageSetDesc: function() {
			let desc = ""
			if (this.mode == "matching") {
				desc += `Images matching the concepts and prediction of pattern ${this.patternIndex}`
			}
			else if (this.mode == "nonmatching") {
				desc += `Images matching the concepts of pattern ${this.patternIndex}, but not matching its prediction`
			}
			else if (this.mode == "wrong") {
				desc += `Images matching the concepts and prediction of pattern ${this.patternIndex}, but incorrectly predicted by the model`
			}
			
			if (this.targetConcept) {
				desc += `, with ${this.targetConcept} activations highlighted`
			}
			return desc
		}
	}, 
	mounted: function() {
		EventBus.$on(Events.DISPLAY_IMAGES, this.displayImages);
		EventBus.$on(Events.CLEAR_IMAGES, this.clearImages);
	}
}
</script>


<style scoped lang="scss">
#images_main {
	display: flex;
	flex-direction: row;
	height: 100%;
	width: 100%;
	/*padding: 20px;*/
}

#concepts_chooser {
	display: flex;
	flex-direction: column;
	background-color: #e8e8e8;
	height: 100%;
	min-width: 20%;
	border-right: 4px solid #999;
}

#images_main_container {
	width: 100%;
}

#image_set_desc {
	height: 15%;
	text-align: center;
}

#images_gallery {
	display: flex;
	flex-direction: row;
	flex-wrap: wrap;
	height: 85%;
	overflow-y: auto;
}

#images_empty {
	display: flex;
	justify-content: center;
	align-items: center;
	width: 100%;
	height: 100%;
}

.image_card {
	width: 20%;
	padding: 8px;
	text-align: center;
}
</style>

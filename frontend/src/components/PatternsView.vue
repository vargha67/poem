<template>
	<div id="patterns_main">
		<div id="patterns_empty" v-if="patterns.length == 0">
			<b-card-text><h5>Set settings in the left and click the button to compute and view the patterns</h5></b-card-text>
		</div>
		
		<b-table v-if="patterns.length > 0" hover bordered responsive sticky-header="42vh" :items="patterns" :fields="fields" primary-key="index" 
			selectable select-mode="single" selected-variant="" @row-selected="onPatternSelected" label-sort-asc="" label-sort-desc="" label-sort-clear="">
			<template v-for="field in fields" v-slot:[`cell(${field.key})`]="data">
				<div v-if="field.key == 'options'" :key="field.key">
					<b-button-group>
						<b-button size="sm" variant="success" v-show="data.item.index == (selectedPattern || {}).index" 
							v-on:click="loadPatternImages('matching')" title="Click to display images matching this pattern's concepts and prediction">
							<!-- :disabled="data.item.confidence == 0.0" -->
							Matching
						</b-button>
						<b-button size="sm" variant="warning" v-show="data.item.index == (selectedPattern || {}).index" 
							v-on:click="loadPatternImages('nonmatching')" title="Click to display images matching this pattern's concepts, but not its prediction">
							<!-- :disabled="data.item.confidence == 1.0" -->
							Non-Matching
						</b-button>
						<b-button size="sm" variant="danger" v-show="data.item.index == (selectedPattern || {}).index" 
							v-on:click="loadPatternImages('wrong')" 
							title="Click to display images matching this pattern's concepts and prediction, but having a different ground-truth label than the CNN prediction">
							<!-- :disabled="data.item.accuracy == 1.0"  -->
							Wrongly-Predicted
						</b-button>
					</b-button-group>
				</div>
				<div v-else-if="field.isConcept" :key="field.key">{{(data.value == 1) ? 'Yes' : (data.value == 0) ? 'No' : ''}}</div>
				<div v-else :key="field.key">{{!isNaN(data.value) && (data.value % 1 != 0) ? data.value.toFixed(2) : data.value}}</div>
			</template>
		</b-table>
	</div>
</template>


<script>
import EventBus from "../EventBus"
import Events from "../Events"

const metaFields = [
	{label: 'Prediction', key: 'pred', sortable: true, thClass: ['text-center', 'align-middle'], tdClass: ['text-center', 'align-middle']},
	{label: 'Support', key: 'support', sortable: true, thClass: ['text-center', 'align-middle'], tdClass: ['text-center', 'align-middle']},
	{label: 'Confidence', key: 'confidence', sortable: true, thClass: ['text-center', 'align-middle'], tdClass: ['text-center', 'align-middle']},
	{label: 'Accuracy', key: 'accuracy', sortable: true, thClass: ['text-center', 'align-middle'], tdClass: ['text-center', 'align-middle']},
	{label: 'Score', key: 'score', sortable: true, thClass: ['text-center', 'align-middle'], tdClass: ['text-center', 'align-middle']},
	{label: 'Method', key: 'method', sortable: true, thClass: ['text-center', 'align-middle'], tdClass: ['text-center', 'align-middle']},
	{label: 'Options', key: 'options', thClass: ['text-center', 'align-middle'], tdClass: ['text-center', 'align-middle']}
]

let concepts = []

export default {
	name: 'PatternsView',
	data () {
		return {
			fields: [],
			patterns: [],
			selectedPattern: {}
		}
	}, 
	methods: {
		displayPatterns: function(patterns) {
			if (!patterns || (patterns.length == 0))
				return
				
			const pat = patterns[0]
			concepts = []
			let metaCols = metaFields.map(f => f.key)
			metaCols.push('index')
			//console.log('Meta columns:', metaCols)
			
			for (let f in pat) {
				if (metaCols.indexOf(f) == -1) {
					concepts.push(f)
				}
			}
			
			concepts.sort()
			//console.log('Concepts:', concepts)
			
			let fields = [{label: 'No.', key: 'index', sortable: true, stickyColumn: true, thClass: ['text-center', 'align-middle'], tdClass: ['text-center', 'align-middle']}]
			for (let c of concepts) {
				fields.push({label: c, key: c, isConcept: true, thClass: ['text-center', 'align-middle'], tdClass: ['text-center', 'align-middle']})
			}
			for (let f of metaFields) {
				fields.push(f)
			}
			
			/*patterns.forEach((p) => {
				let cellVariants = {}
				concepts.forEach((c) => {
					const val = p[c]
					if (val == 1)
						cellVariants[c] = 'success'
					else if (val == 0)
						cellVariants[c] = 'warning'
				})
				p._cellVariants = cellVariants
			})*/
			
			this.fields = fields
			this.patterns = patterns
			//console.log('Fields:', fields)
		}, 
		onPatternSelected: function(patterns_list) {
			this.selectedPattern = patterns_list[0]
			//console.log('Pattern selected:', this.selectedPattern)
		},
		loadPatternImages: function(mode) {
			if (!this.selectedPattern || !this.selectedPattern.index)
				return
		
			const patternIndex = this.selectedPattern.index
			const activatedConcepts = concepts.filter((c) => {
				if (this.selectedPattern[c] == 1)
					return true
				return false
			})
			//console.log(`Activated concepts for pattern ${patternIndex}: ${activatedConcepts}`)
			
			EventBus.$emit(Events.LOAD_IMAGES_INFO, patternIndex, mode, activatedConcepts)
		}
	},
	mounted: function() {
		EventBus.$on(Events.DISPLAY_PATTERNS, this.displayPatterns);
	}
}
</script>


<style scoped lang="scss">
#patterns_main {
	width: 100%;
	height: 100%;
	overflow-x: hidden;
	/*padding: 20px;*/
}

#patterns_empty {
	display: flex;
	justify-content: center;
	align-items: center;
	width: 100%;
	height: 100%;
}
</style>

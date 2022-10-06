<template>
	<div id="settings_main">
		<b-card-body class="settings_section">
			<b-card-text>Dataset:</b-card-text>
			<b-form-select v-model="dataset" @change="datasetChanged">
                <b-form-select-option disabled :value="null">-- Select a target dataset --</b-form-select-option>
                <b-form-select-option v-for="item in datasetOptions" :value="item.value" :key="item.value">
                    {{item.title}}
                </b-form-select-option>
            </b-form-select>
		</b-card-body>
		
		<!--<div class="vertical_line settings_section"></div>-->
		<hr style="margin: 8px;"/>
		
		<b-card-body class="settings_section">
			<b-card-text>CNN Model:</b-card-text>
			<b-form-select v-model="model">
                <b-form-select-option disabled :value="null">-- Select a CNN model architecture --</b-form-select-option>
                <b-form-select-option v-for="item in modelOptions" :value="item.value" :key="item.value">
                    {{item.title}}
                </b-form-select-option>
            </b-form-select>
		</b-card-body>
		
		<hr style="margin: 8px;"/>
		
		<b-card-body class="settings_section">
			<b-card-text>Pattern Mining Methods:</b-card-text>
			<b-form-checkbox-group v-model="ruleMethods" @change="ruleMethodsChanged" stacked>
                <b-form-checkbox v-for="item in ruleMethodOptions" :value="item.value" :key="item.value">
                    {{item.title}}
                </b-form-checkbox>
            </b-form-checkbox-group>
		</b-card-body>
		
		<hr style="margin: 8px;" v-if="ruleMethodParamOptions.length > 0" />
		
		<b-card-body class="settings_section" v-if="ruleMethodParamOptions.length > 0">
			<b-card-text>Parameters of Pattern Mining Methods:</b-card-text>
			<b-row v-for="item in ruleMethodParamOptions" :key="item.key">
				<b-col sm="8">
					<label :for="item.key">{{item.title}}</label>
				</b-col>
				<b-col sm="4">
					<!-- b-form-input :id="item.key" type="number" v-model="item.value" :min="item.min" :max="item.max" :step="item.step"></b-form-input> -->
					<b-form-select v-model="item.value">
				        <b-form-select-option v-for="opt in item.options" :value="opt" :key="opt">
				            {{opt}}
				        </b-form-select-option>
				    </b-form-select>
				</b-col>
			</b-row>
		</b-card-body>
		
		<b-card-body class="settings_section" style="text-align: center;">
			<b-button variant="primary" id="start_button" v-on:click="startProcess">Compute Patterns</b-button>
		</b-card-body>
		
		<div class="settings_section" style="flex-grow: 10;">&nbsp;</div>
	</div>
</template>


<script>
import EventBus from "../EventBus"
import Events from "../Events"

const datasetOptions = [
	{title: 'Places (Bedroom, Kitchen, Livingroom)', value: 'places_bedroom_kitchen_livingroom'},
	{title: 'Places (Coffeeshop, Restaurant)', value: 'places_coffeeshop_restaurant'},
	{title: 'ImageNet (Minivan, Pickup)', value: 'imagenet_minivan_pickup'},
	//{title: 'Choose another dataset ...', value: 'custom'}
]

const modelOptions = [
	{title: 'Resnet-18', value: 'resnet18'},
	{title: 'Resnet-50', value: 'resnet50'},
	{title: 'VGG-16', value: 'vgg16'}
]

const ruleMethodOptions = [
	{title: 'Explanation Tables', value: 'exp'},
	{title: 'Interpretable Decision Sets (IDS)', value: 'ids'},
	{title: 'CART Decision Trees', value: 'cart'}
]

/*const ruleMethodParamOptions = [
	{title: 'Exp. Tables number of patterns', key: 'expNumPatterns', method: 'exp', value: 10, min: 1, max: 20, step: 1},
	{title: 'IDS min support ratio', key: 'idsMinSupport', method: 'ids', value: 0.01, min: 0.0, max: 1.0, step: 0.01}, 
	{title: 'CART min samples per leaf ratio', key: 'cartMinSamplesLeaf', method: 'cart', value: 0.03, min: 0.01, max: 1.0, step: 0.01}
]*/

const ruleMethodParamOptions = [
	//{title: 'Exp. Tables max number of patterns', key: 'expNumPatterns', method: 'exp', options: [5, 10, 15, 20], value: 10},
	{title: 'Exp. Tables min support', key: 'expMinSupport', method: 'exp', options: [0.01, 0.03, 0.05, 0.1, 0.15, 0.2], value: 0.01}, 
	{title: 'IDS min support', key: 'idsMinSupport', method: 'ids', options: [0.01, 0.03, 0.05, 0.1, 0.15, 0.2], value: 0.01}, 
	{title: 'CART min support (min samples per leaf)', key: 'cartMinSamplesLeaf', method: 'cart', options: [0.01, 0.03, 0.05, 0.1, 0.15, 0.2], value: 0.01}
]

export default {
	name: 'SettingsView',
	data () {
		return {
			dataset: null,
			model: null,
			ruleMethods: [],
			datasetOptions: datasetOptions,
			modelOptions: modelOptions,
			ruleMethodOptions: ruleMethodOptions,
			ruleMethodParamOptions: []
		}
	}, 
	methods: {
		datasetChanged: function() {
			if (this.dataset == 'custom') {
				// Allow user to browse disk and choose the dataset root directory
			}
		}, 
		ruleMethodsChanged: function() {
			this.ruleMethodParamOptions = ruleMethodParamOptions.filter((item) => {
				if (this.ruleMethods.indexOf(item.method) != -1)
					return true
				return false
			})
		},
		startProcess: function() {
			const ruleMethodParams = this.ruleMethodParamOptions.map(item => {
				return {key: item.key, value: item.value}
			})
			EventBus.$emit(Events.START_PROCESS, this.dataset, this.model, this.ruleMethods, ruleMethodParams)
		}
	}
}
</script>


<style scoped lang="scss">
#settings_main {
	display: flex;
	flex-direction: column;
	justify-content: flex-start;
	background-color: #e8e8e8;
	height: 100%;
	padding: 20px;
	overflow-y: auto;
}

.settings_section {
	
}

.vertical_line {
	border: 1px solid #aaa;
	margin: 8px;
}
</style>

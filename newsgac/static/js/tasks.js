function mitt(all) {
	all = all || Object.create(null);
	return {
		on(type, handler) {
			(all[type] || (all[type] = [])).push(handler);
		},

		off(type, handler) {
			if (all[type]) {
				all[type].splice(all[type].indexOf(handler) >>> 0, 1);
			}
		},

		emit(type, evt) {
			(all[type] || []).slice().map((handler) => { handler(evt); });
			(all['*'] || []).slice().map((handler) => { handler(type, evt); });
		}
	};
}

const m = mitt();
const ws = new WebSocket(`ws://${window.location.hostname}:5051`);

window.initTask = (elm) => {
    const attrs = JSON.parse(elm.innerHTML);
    const vue = new Vue({
        el: elm,
        template: `
    <div :class="['task', status]">
        {{ status }}
        <div v-if="progress && subProgress.progress !== 1" v-for="subProgress in progress">
            <progress :value="subProgress.progress"></progress> <span class="task--sub">({{ subProgress.name }})</span> {{ (subProgress.progress * 100).toFixed(0) }} &percnt;
        </div>
    </div>
`,
        methods: {
            onMessage: function(message) {
                const data = JSON.parse(message.data);
                if (data.id && data.id === this.id) {
                    this.status = data.state;
                    if (data.result.progress) {
                        this.progress = data.result.progress;
                    }
                }
            }
        },
        mounted: function () {
            if (['FAILURE', 'SUCCESS', 'REVOKED'].indexOf(this.status) === -1) {
                ws.send(JSON.stringify({type: 'watch_task', task_id: this.id}));
                m.on('message', this.onMessage);
            }
        },
        data: attrs,
        computed: {
            merged_tasks: function () {
                return this.tasks.map(task => ({...task, currentResult: task.results[task.results.length - 1]}));
            }
        }
    });
};


document.addEventListener('DOMContentLoaded', contentLoadedEvent => {
    ws.onopen = () => {
        ws.onerror = () => null;
        [].forEach.call(document.querySelectorAll('.task.hidden'), initTask);
        ws.send(JSON.stringify({type: 'watch_new'}));
    };
    ws.onerror = () => {
        [].forEach.call(document.querySelectorAll('.task.hidden'), initTask);
    };
    ws.onmessage = message => m.emit('message', message);
});

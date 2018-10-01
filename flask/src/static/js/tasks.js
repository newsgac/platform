document.addEventListener('DOMContentLoaded', contentLoadedEvent => {
    const vm1 = new Vue({
        el: '#tasks_root',
        template: `
<div v-if="!hidden" id="tasks_root">
    <button type="button" class="btn btn-close" @click="hidden = true">Close</button>
    <div v-if="!hidden" class="task" v-for="task in merged_tasks">
        {{ task.name }}
        <div v-if="task.status === 'PENDING'">Queued</div>
        <progress v-else-if="task.status === 'SUCCESS'" class="completed" value="1"></progress>
        <template v-else-if="task.status === 'FAILURE'">
            <progress class="failure" value="1"></progress> Failed :(
        </template>
        <template v-else-if="task.currentResult && task.currentResult.result.progress">
           <progress :value="task.currentResult.result.progress"></progress> 
           &nbsp; {{(100 * task.currentResult.result.progress).toFixed(0)}} &percnt;
       </template>
        <progress v-else>?</progress>
    </div>
</div>
`,
        data: {
            tasks: [ ],
            hidden: true
        },
        computed: {
            merged_tasks: function() {
                return this.tasks.map(task => ({ ...task, currentResult: task.results[task.results.length -1]}));
            }
        }
    });

    const vm2 = new Vue({
        el: '#tasks_button',
        template: `<span>{{runningTasks}} tasks</span>`,
        data: {
            tasks: [ ],
        },
        computed: {
            runningTasks: function() {
                return this.tasks.filter(task => task.status !== 'SUCCESS' && task.status !== 'FAILURE').length;
            }
        }
    });

    document.getElementById('tasks_trigger').addEventListener('click', () => vm1.$data.hidden = false);

    const loopFetchData = () => {
        fetch('/tasks/')
            .then(r => r.json())
            .then(tasks => {
                vm1.tasks = tasks;
                vm2.tasks = tasks;
            });
        setTimeout(loopFetchData, 5000)
    };
    loopFetchData();
});

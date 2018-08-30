document.addEventListener('DOMContentLoaded', contentLoadedEvent => {
    const vm1 = new Vue({
        el: '#tasks_root',
        template: `
<div v-if="!hidden" id="tasks_root">
    <button type="button" class="btn btn-close" @click="hidden = true">Close</button>
    <div v-if="!hidden" class="task" v-for="task in tasks">
        {{ task.task_name }}
        <progress v-if="task.status === 'SUCCESS'" class="completed" value="1"></progress>
        <template v-else-if="task.status === 'FAILURE'">
            <progress class="failure" value="1"></progress> Failed :(
        </template>
        <template v-else-if="task.result && task.result.progress !== undefined">
           <progress :value="task.result.progress"></progress> {{(100 * task.result.progress).toFixed(0)}} &percnt;
       </template>
        <progress v-else>?</progress>
    </div>
</div>
`,
        data: {
            tasks: [ ],
            hidden: true
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
                return this.tasks.filter(task => task.status !== 'STARTED' && task.status !== 'SUCCESS' && task.status !== 'FAILURE').length;
            }
        }
    });

    document.getElementById('tasks_trigger').addEventListener('click', () => vm1.$data.hidden = false);

    const loopFetchData = () => {
        fetch('/tasks')
            .then(r => r.json())
            .then(tasks => {
                vm1.tasks = tasks;
                vm2.tasks = tasks;
            });
        setTimeout(loopFetchData, 5000)
    };
    loopFetchData();
});

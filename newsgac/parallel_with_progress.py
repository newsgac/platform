import time

from sklearn.externals.joblib import Parallel
from sklearn.externals.joblib.parallel import BatchCompletionCallBack


# Extends Parallel with ws progress callback (# of jobs done)
class ParallelWithProgress(Parallel):
    def __init__(self, n_jobs=1, backend=None, verbose=0, timeout=None, pre_dispatch='2 * n_jobs', batch_size='auto',
                 temp_folder=None, max_nbytes='1M', mmap_mode='r', progress_callback=None):

        super(ParallelWithProgress, self).__init__(n_jobs, backend, verbose, timeout, pre_dispatch, batch_size,
                                                   temp_folder, max_nbytes, mmap_mode)

        self.progress_callback = progress_callback

    def _dispatch(self, batch):
        if self._aborting:
            return

        self.n_dispatched_tasks += len(batch)
        self.n_dispatched_batches += 1

        dispatch_timestamp = time.time()
        cb = BatchCompletionCallBackWithProgress(dispatch_timestamp, len(batch), self)
        job = self._backend.apply_async(batch, callback=cb)
        self._jobs.append(job)


class BatchCompletionCallBackWithProgress(BatchCompletionCallBack):
    def __call__(self, out):
        self.parallel.n_completed_tasks += self.batch_size
        this_batch_duration = time.time() - self.dispatch_timestamp

        self.parallel._backend.batch_completed(self.batch_size,
                                               this_batch_duration)
        self.parallel.print_progress()
        if self.parallel.progress_callback:
            self.parallel.progress_callback(self.parallel.n_completed_tasks)

        if self.parallel._original_iterator is not None:
            self.parallel.dispatch_next()
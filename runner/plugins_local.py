from runner.data_processing import AuditRunnerProvider
from runner.document_validation import (DocumentValidatorProvider,
                                        ValidationError)


class PlainTextValidator(DocumentValidatorProvider):

    def validate(self, file_obj):
       "Assert file has at least one line"
       line = file_obj.readline()
       if not line:
           raise ValidationError


class MinimalAuditRunner(AuditRunnerProvider):

    def file_manager(self):
        # get files from job
        job = self.job_cls.objects.get(pk=self.job_pk)
        docs = job.documents.all()
        # arrange files in a list and return it
        files = [document.file.file.name for document in docs]
        return files

    def process_data(self):
        # just show some info about the job

        job = self.job_cls.objects.get(pk=self.job_pk)
        audit_name = job.audit.name

        # use self.workspace to save files
        final_file_path = '%s/%s' % (self.workspace, 'test_file.txt')
        with open(final_file_path, 'w') as final_file:
            final_file.write('Result file for Job #%d\n' % (self.job_pk,))
            final_file.write('Audit name: %s\n\n' % (audit_name,))
            final_file.write('Job files:\n')
            for f in self.files:
                final_file.write('\t' +  f + '\n')

        # return the final file full-path
        return final_file_path

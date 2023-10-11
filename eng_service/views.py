from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from django.views.generic import TemplateView, FormView, CreateView, UpdateView
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from eng_service.ENG_FIX_logic import fixer, EngRephr
from eng_service.forms import EngFixerForm
from eng_service.local_lib.google_translate import T
from eng_service.models import EngFixer
# from stripe_payments.services import create_stripe_session
import logging


# TODO LIST BY USER
class EngMainView(TemplateView):
    template_name = "Eng_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['data_list'] = EngFixer.objects.all()
        return context


class CheckENGView(CreateView):  # LoginRequiredMixin
    form_class = EngFixerForm
    template_name = "Eng_form.html"

    # success_url = reverse_lazy('stripe_service:eng1_get', kwargs={'pk': self.object.pk})

    # after fixer
    def get_success_url(self):
        return reverse('eng_service:eng_get', args=(self.object.id,))  # lazy?

    # initial = {'text': 'example'}
    # success_url = reverse_lazy('form_msg:send_msg')
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['title'] = "📨 Send message form"
    #     context['btn_caption'] = "Send"
    #     context['table_data'] = Message.objects.select_related().order_by('-created_date')[:5]
    #
    #     return context

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['description'] = pprint.pformat(self.object.fixed_result_JSON)
    #     return context

    # def post(self, request, *args, **kwargs):
    #     pass

    """AFTER POST METHOD VALIDATION
    def post(self, request, *args, **kwargs):
        form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
    
    """

    # TODO SAVE UNIQUE, FIX LOGIC PROCESS

    def form_invalid(self, form):
        # TODO

        # form.add_error(None, '123')
        # if 'non_field_errors' in form.errors:
        #     for error in form.errors['non_field_errors']:
        #         if isinstance(error, ValidationError): #and 'unique' in error.message:
        #             # Handle the Unique constraint error here
        #             # For example, you can add a custom error message to the form
        #             form.add_error(None, 'This record violates a unique constraint.')
        #             break

        err_ = form.errors['input_sentence'].data[0]
        print(isinstance(err_, ValidationError))

        # form.add_error(None, '123')

        print(form.fields['input_sentence'])
        print(form.error_class)

        print('ERR FORM INVALID')
        return super(CheckENGView, self).form_invalid(form)

    def form_valid(self, form) -> HttpResponseRedirect:
        obj: EngFixer = form.save(commit=False)

        # TODO !!! form.cleaned_data

        # obj.author = self.request.user

        # todo if in cache or db then redirect
        # return redirect('stripe_service:eng_get', obj.id)
        logger = logging.getLogger()
        # item = EngFixer.objects.get(input_sentence=obj.input_sentence)

        # existing
        db_item = EngFixer.objects.filter(input_sentence=obj.input_sentence).first()
        # item = EngFixer.objects.filter(input_sentence=obj.input_sentence).exists()

        if db_item:
            logger.warning(f'using cache: id:{db_item.id}')
            return redirect('eng_service:eng_get', db_item.id,
                            # use_cache=True
                            )

        # todo MAIN FIXER logic
        fix = fixer(obj.input_sentence)
        obj.fixed_sentence = fix.get('text')
        obj.fixed_result_JSON = fix.get('corrections')
        print(obj.fixed_sentence)

        # rephraser
        rephrases = EngRephr().get_rephrased_sentences(input_str=obj.input_sentence)
        if rephrases:
            obj.rephrases_list = rephrases

        # translate
        tr_input = T().get_ru_from_eng(text=obj.input_sentence)
        tr_correct = T().get_ru_from_eng(text=obj.fixed_sentence)

        # todo
        obj.translated_RU = f"{tr_input} ->\n{tr_correct}"
        # obj.translated_RU = T().get_ru_from_eng(text=obj.input_sentence)

        # save and redirect
        return super(CheckENGView, self).form_valid(form)

    # def form_invalid(self, form):
    #     return super(CheckENGView, self).form_invalid(form)


class CheckENGViewUpdate(UpdateView):  # LoginRequiredMixin
    """display data by get pk + CONTEXT FOR UPDATEVIEW"""

    """UPDATE VIEW FOR FORMS
    eng_get/<int:pk>/
    """

    model = EngFixer
    form_class = EngFixerForm
    template_name = "Eng_form.html"

    # success_url = reverse_lazy('form_msg:send_msg')

    def get_object(self, *args, **kwargs):
        obj = super(CheckENGViewUpdate, self).get_object(*args, **kwargs)
        # if obj.author != self.request.user:
        #     raise PermissionDenied()  # or Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # json to text
        # context['description'] = pprint.pformat(self.object.fixed_result_JSON, indent=4).replace('\n', '<br>')

        # TODO
        suggestions_rows = []
        data = list(self.object.fixed_result_JSON)
        if data:
            for item in data:
                # input
                text = item.get('mistakeText')
                long_description = item.get('longDescription')

                # грамм ошибка
                short_description = item.get('shortDescription')

                # suggestions
                suggestions = item.get('suggestions')
                """'suggestions': [
                                    {
                                        'text': 'I feel',
                                        'category': 'Verb'
                                    },
                                    {
                                        'text': "I'm feel",
                                        'category': 'Spelling'
                                    },
                                    {
                                        'text': "I'm feeling",
                                        'category': 'Verb'
                                    },
                                    {
                                        'text': 'I felt',
                                        'category': 'Verb'
                                    }
                                ],"""

                FIXED_TEXT = ""

                # sugg_list = []
                # if item:
                #     for s in suggestions:
                #         sugg_list.append(s)
                # if sugg_list:
                #     FIXED_TEXT = sugg_list[0]['text']
                #     # sugg_list = '\n'.join(map(str, sugg_list))
                #     sugg_list = '\n'.join(f"{s['text']} ({s['category']}, {s.get('definition', '')})" for s in sugg_list)

                if suggestions:
                    FIXED_TEXT = suggestions[0]['text']

                    # sugg_list = '\n'.join(map(str, sugg_list))
                    sugg_string = '\n'.join(f"{s['text']} ({s['category']}, {s.get('definition', '')})" for s in suggestions)
                else:
                    sugg_string = ""

                suggestions_rows.append((text, FIXED_TEXT, long_description, short_description, sugg_string))

                    # fix_text = item.get('text')
                    # category = item.get('category')
                    # definition = item.get('definition')
                # suggestions_rows.append((text, fix_text, category, definition, short_description, long_description))


        context['suggestions_rows'] = suggestions_rows
        context['rephrases_list'] = '\n'.join(self.object.rephrases_list) if self.object.rephrases_list else None

        context['translate'] = self.object.translated_RU

        # rephr
        # data = get_rephrased(input_str=None)

        return context

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['title'] = "📨 Send message form"
    #     context['btn_caption'] = "Send"
    #     context['table_data'] = Message.objects.select_related().order_by('-created_date')[:5]
    #
    #     return context

    def form_valid(self, form):
        # obj = form.save(commit=False)
        # obj.author = self.request.user

        return super(CheckENGViewUpdate, self).form_valid(form)


####################################################################################################################

# for mix detail
# https://stackoverflow.com/questions/45659986/django-implementing-a-form-within-a-generic-detailview



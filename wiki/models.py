
from django.db import models
from .formular import *


# Create your models here.


class Issue(models.Model):
    id = models.IntegerField(primary_key=True)
    issue_title = models.CharField(max_length=300)
    issue_info = models.TextField(max_length=500)
    lang = models.TextField(max_length=10)


class Position(models.Model):
    id = models.IntegerField(primary_key=True)
    issue = models.ManyToManyField(Issue)
    statement = models.ForeignKey('Statement', on_delete=models.CASCADE, related_name='statement_position')
    statement_below = models.ManyToManyField('Statement', related_name='statementsBelow')
    acceptance_score = models.FloatField(null=True)

    def __str__(self):
        return self.statement.__str__()

    def position_acceptance(self):
        self.statement.statement_acceptance()
        self.acceptance_score = self.statement.acceptance * 100
        self.save()


class Argument(models.Model):
    id = models.IntegerField(primary_key=True)
    text = models.TextField(null=True)
    upVotes = models.IntegerField()
    context_assessment = models.BooleanField()
    downVotes = models.IntegerField()
    lang = models.TextField()
    isSupportive = models.BooleanField()
    date = models.DateTimeField()
    under_position = models.ManyToManyField(Position)
    keywords = models.ManyToManyField('Keyword')
    concepts = models.ManyToManyField('Concept')
    categories = models.ManyToManyField('Category')
    information = models.ManyToManyField('Information')
    emotion = models.ForeignKey('Emotion', on_delete=models.CASCADE, null=True)
    attacked_argument = models.ForeignKey('Argument',
                                          on_delete=models.CASCADE,
                                          related_name='attackedargument',
                                          null=True)
    conclusion = models.ForeignKey('Conclusion',
                                   on_delete=models.CASCADE,
                                   null=True)
    premise_group = models.ForeignKey('PremiseGroup', on_delete=models.CASCADE)
    type = models.TextField(null=True)
    type_text = models.TextField(null=True)
    argument_acceptance = models.FloatField(null=True)
    conclusion_acceptability = models.FloatField(null=True)
    f_r_ease = models.IntegerField(null=True)
    ari = models.IntegerField(null=True)
    sound = models.FilePathField(null=True)
    sentiment_accuracy = models.FloatField(null=True)

    def plain_string(self):
        premise = self.premise_group.__str__()
        conclusion = self.conclusion.__str__()
        if self.conclusion is None:
            conclusion = '. ' + self.attacked_argument.plain_string()
        return premise + ' ' + conclusion

    def __str__(self):
        premise = self.premise_group.__str__()
        conclusion = self.conclusion.__str__()
        if self.conclusion is None:
            conclusion = self.attacked_argument.__str__()
        return self.type_text.join([premise, conclusion])

    @property
    def save_text(self):
        self.text = 'Regarding that ' + self.__str__()
        self.save()

    @property
    def sentiment(self):
        if self.sentiment_accuracy == 0:
            return 'neutral'
        if self.sentiment_accuracy > 0.0:
            return 'positive'
        else:
            return 'negative'

    @property
    def acceptance(self):
        return self.argument_acceptance * 100

    @property
    def attacked_by(self):
        return Argument.objects.filter(attacked_argument=self)

    @property
    def under_issues(self):
        issues = []
        for pos in self.under_position.all():
            for issue in pos.issue.all():
                issues.append(issue)
        return list(set(issues))

    def has_full_information(self):
        for information in self.information.all():
            if information.full:
                return True
        return False

    def has_ambi_information(self):
        for information in self.information.all():
            if information.ambivalent:
                return True
        return False

    def conclusion_acceptability(self):
        self.premise_group.premise_acceptance()
        return self.premise_group.premise_group_acceptance * self.conditional_acceptability()

    def conditional_acceptability(self):
        c_a = 1
        for argument in self.attacked_by:
            argument.conclusion_acceptability()
            c_a = reliability(c_a, argument.conclusion_acceptability())
        return c_a

    def argument_acceptability(self):
        self.argument_acceptance = self.conclusion_acceptability()
        if self.isSupportive is False:
            self.argument_acceptance = 1 - self.argument_acceptance
        self.save()


class Statement(models.Model):
    id = models.IntegerField(primary_key=True)
    isPosition = models.BooleanField()
    lang = models.TextField()
    new_calculation = models.IntegerField(default=0)
    statement_text = models.TextField(null=True)
    acceptance = models.FloatField(null=True)

    def __str__(self):
        return self.statement_text

    def statement_acceptance(self):
        if self.conclusion_set.all().first() is not None:
            self.new_calculation += 1
            if self.new_calculation >= 2:
                self.acceptance = 0.5
            else:
                self.conclusion_set.all().first().conclusion_acceptance()
                self.acceptance = self.conclusion_set.all().first().conclusion_acceptability
        else:
            self.acceptance = 0.75
        self.save()


class Conclusion(models.Model):
    id = models.IntegerField(primary_key=True)
    rebuts = models.IntegerField()
    supports = models.IntegerField()
    undercuts = models.IntegerField()
    statement = models.ForeignKey(Statement, on_delete=models.CASCADE)
    information = models.ManyToManyField('Information')
    inference_score = models.FloatField(null=True)
    conclusion_acceptability = models.FloatField(null=True)

    def __str__(self):
        return self.statement.__str__()

    @property
    def positive_inference(self):
        return self.argument_set.all().filter(isSupportive=True).count()

    @property
    def negative_inference(self):
        return self.argument_set.all().exclude(isSupportive=True).count()

    def con_convergent(self):
        result = 0.5
        for argument in self.argument_set.all().filter(isSupportive=False):
            argument.argument_acceptability()
            if argument.argument_acceptance < 0.5:
                result = 1 - acceptability(1 - result, 1 - argument.argument_acceptance)
        return result

    def pro_convergent(self):
        result = 0.5
        for argument in self.argument_set.all().filter(isSupportive=True):
            argument.argument_acceptability()
            if argument.argument_acceptance > 0.5:
                result = acceptability(result, argument.argument_acceptance)
        return result

    def conductive(self):
        strength_pro = self.pro_convergent()
        strength_con = self.con_convergent()
        if strength_pro == 1:
            return 1
        if strength_con == 0:
            return 0
        if strength_pro == 1 and strength_con == 0:
            return None
        return strength_pro + strength_con - (1 / 2)

    def conclusion_acceptance(self):
        n_of_arguments = self.argument_set.all().count()  # rebuts+supports+undercuts
        n_of_supports = self.argument_set.all().filter(isSupportive=True).count()  # supports
        if n_of_arguments is 1:
            self.argument_set.first().conclusion_acceptability()
        if n_of_arguments == n_of_supports:
            self.conclusion_acceptability = self.pro_convergent()
        if n_of_supports == 0:
            self.conclusion_acceptability = self.con_convergent()
        if n_of_arguments != n_of_supports:
            self.conclusion_acceptability = self.conductive()
        self.save()


class PremiseGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    information = models.ManyToManyField('Information')
    positive_inference = models.IntegerField(null=True)
    negative_inference = models.IntegerField(null=True)
    ratio_inference = models.FloatField(null=True)
    premise_group_acceptance = models.FloatField(null=True)

    def __str__(self):
        return ', '.join([premise.__str__() for premise in self.premise_set.all()])

    def premise_acceptance(self):
        score = 1
        for premise in self.premise_set.all():
            premise.statement.statement_acceptance()
            score *= premise.statement.acceptance
        if score <= 0.5:
            score = 0.5
        self.premise_group_acceptance = score
        self.save()


class Premise(models.Model):
    id = models.IntegerField(primary_key=True)
    premiseGroup = models.ForeignKey(PremiseGroup, on_delete=models.CASCADE)
    statement = models.ForeignKey(Statement, on_delete=models.CASCADE)

    def __str__(self):
        return self.statement.__str__()


class Information(models.Model):
    id = models.IntegerField(primary_key=True)
    word = models.TextField()
    title = models.TextField()
    description = models.TextField(null=True)
    summary = models.TextField(null=True)
    link = models.TextField()
    fullInfo = models.BooleanField(null=True)
    acad_score = models.ForeignKey('AcadScore', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.word).replace("_", " ")

    @property
    def full(self):
        return Information.objects.filter(id=self.id).exclude(summary=None)

    @property
    def ambivalent(self):
        return Information.objects.filter(id=self.id).filter(summary=None)


class AcadScore(models.Model):
    his = models.DecimalField(decimal_places=2, max_digits=4)
    edu = models.DecimalField(decimal_places=2, max_digits=4)
    soc = models.DecimalField(decimal_places=2, max_digits=4)
    bus = models.DecimalField(decimal_places=2, max_digits=4)
    med = models.DecimalField(decimal_places=2, max_digits=4)
    hum = models.DecimalField(decimal_places=2, max_digits=4)
    sci = models.DecimalField(decimal_places=2, max_digits=4)
    law = models.DecimalField(decimal_places=2, max_digits=4)
    phil = models.DecimalField(decimal_places=2, max_digits=4)
    linecol = models.TextField()
    background = models.TextField()


class News(models.Model):
    source = models.TextField()
    date = models.DateField()
    title = models.TextField()
    type = models.TextField()
    description = models.TextField()
    url = models.TextField()


class Concept(models.Model):
    conceptname = models.ForeignKey('ConceptText', on_delete=models.CASCADE)
    relevance = models.FloatField()

    def __str__(self):
        return self.conceptname.__str__()


class ConceptText(models.Model):
    text = models.TextField()
    explanation = models.TextField()

    def __str__(self):
        return self.text


class Category(models.Model):
    categorylabel = models.ForeignKey('CategoryLabel', on_delete=models.CASCADE)
    relevance = models.FloatField()

    def __str__(self):
        return self.categorylabel.__str__()


class CategoryLabel(models.Model):
    label = models.TextField(unique=True)

    def __str__(self):
        return self.label


class Keyword(models.Model):
    keywordtext = models.ForeignKey('KeywordText', on_delete=models.CASCADE)
    relevance = models.FloatField()

    def __str__(self):
        return self.keywordtext.__str__()


class KeywordText(models.Model):
    news = models.ManyToManyField(News)
    text = models.TextField()

    def __str__(self):
        return self.text


class Emotion(models.Model):
    sadness = models.DecimalField(decimal_places=2, max_digits=4)
    joy = models.DecimalField(decimal_places=2, max_digits=4)
    fear = models.DecimalField(decimal_places=2, max_digits=4)
    disgust = models.DecimalField(decimal_places=2, max_digits=4)
    anger = models.DecimalField(decimal_places=2, max_digits=4)
    linecol = models.TextField(default='rgba(102,255,102,0.3)')
    background = models.TextField(default='rgba(102,255,102,0.3)')

    @property
    def sadness_label(self):
        return 'sadness'

    @property
    def joy_label(self):
        return 'joy'

    @property
    def fear_label(self):
        return 'fear'

    @property
    def disgust_label(self):
        return 'disgust'

    @property
    def anger_label(self):
        return 'anger'

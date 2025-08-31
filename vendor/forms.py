from django import forms
from store.models import Product
from vendor.models import Advertisement
from category.models import Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'product_name', 'slug', 'description', 'price',
            'images', 'stock', 'is_available', 'category'
        ]
        widgets = {
            'is_available': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for field_name, bound_field in self.fields.items():
            if isinstance(bound_field.widget, forms.CheckboxInput):
                bound_field.widget.attrs.update({
                    'class': 'form-check-input mx-5',
                })
                # Ensure no width style on checkbox
                if 'style' in bound_field.widget.attrs:
                    del bound_field.widget.attrs['style']
            else:
                bound_field.widget.attrs.update({
                    'class': 'form-control mx-5',
                    'style': 'max-width: 90%;'
                })


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = [
            'category_name', 'slug', 'description','cat_image'
        ]

    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            # self.fields[field].widget.attrs['class']  = 'form-control'
            self.fields[field].widget.attrs.update({
                'class': 'form-control mx-5',  
                'style': 'max-width: 90%;'    
            })




class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['ad_name', 'image']

    def __init__(self, *args, **kwargs):
        super(AdvertisementForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control my-2',
            })

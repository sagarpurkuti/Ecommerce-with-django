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

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            # self.fields[field].widget.attrs['class']  = 'form-control'
            self.fields[field].widget.attrs.update({
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

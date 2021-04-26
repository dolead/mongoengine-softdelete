[![CircleCI](https://circleci.com/gh/dolead/mongoengine-softdelete.svg?style=shield)](https://app.circleci.com/pipelines/github/dolead/mongoengine-softdelete) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/6d09806a72f44b65aeb72cbbafa9c986)](https://www.codacy.com/gh/dolead/mongoengine-softdelete/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dolead/mongoengine-softdelete&amp;utm_campaign=Badge_Grade)

# MongoEngine Soft Delete

Make a document soft deletable.

## Installation

Install `mongoengine-softdelete` through pip as usual:

    pip install mongoengine-softdelete

## Usage

Here is an example on how to use a soft deletable document:

    from mongoengine_softdelete.document import SoftDeleteNoCacheDocument    

    class IceCream(SoftDeleteNoCacheDocument):
        meta = {
            'collection': 'ice_cream',
            'soft_delete': {'deleted': True},
            'indexes': [ 'flavor' ],
            'strict': False
        }

        flavor = fields.StringField(required=True)
        color = fields.StringField(required=True)
        price = fields.FloatField(default=0)
        created_at = fields.DateTimeField()

        # Declare the field used to check if the record is soft deleted
        # this field must also be reported in the `meta['soft_delete']` dict
        deleted = fields.BooleanField(default=False)

    # Save a new document
    ice = IceCream(flavor="Vanilla", color="White").save()
    assert not ice.is_soft_deleted

    # Mark the document as soft deleted
    ice.soft_delete()
    assert len(IceCream.objects()) == 0
    assert ice.is_soft_deleted

    # Soft undelete the document
    ice.soft_undelete()
    assert len(IceCream.objects()) > 0
    assert not ice.is_soft_deleted

## Tests

The test suit requires that you run a local instance of MongoDB on the standard
port and have `pytest` installed.  
You can run tests with the `pytest` command or with `make test`.

Linting is done with `mypy` and `pycodestyle` with the `make lint` command.

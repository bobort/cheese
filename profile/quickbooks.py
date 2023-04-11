import datetime

from django.conf import settings
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks
from quickbooks.objects import Customer, Invoice, SalesItemLine, Item, SalesItemLineDetail, Account, Term

auth_client = AuthClient(**settings.QUICKBOOKS)

# Prepare scopes
scopes = [Scopes.ACCOUNTING, ]

# Get authorization URL
auth_url = auth_client.get_authorization_url(scopes)

client = QuickBooks(
    auth_client=auth_client,
    refresh_token=settings.QB_REFRESH_TOKEN,
    company_id=settings.QB_REALM_ID,  # realm id
)


def get_customer(student):
    """
        Return the Quickbooks customer object from our Student object
        Creates a new customer if one does not exist.
    """
    customer = Customer.filter(max_results=1, FamilyName=student.last_name, GivenName=student.first_name, qb=client)
    if customer:
        customer = customer[0]
    else:
        customer = Customer()
        customer.FamilyName = student.last_name
        customer.GivenName = student.first_name
        customer.save(qb=client)
    return customer


def get_item_account(account_name):
    """
        Return the Quickbooks IncomeAccount for an Item object from our Product object
        Creates a new IncomeAccount if one does not exist.
    """
    acct = Account.filter(max_results=1, Name=account_name, AccountSubType="ServiceFeeIncome", qb=client)
    if acct:
        acct = acct[0]
    else:
        acct = Account()
        acct.AccountSubType = "ServiceFeeIncome"
        acct.Name = account_name
        acct.save(qb=client)
    return acct


def get_item(product):
    """
        Return the Quickbooks item object from our Product object
        Creates a new product if one does not exist.
    """
    account = get_item_account(product.account_name).to_ref()
    item = Item.filter(
        max_results=1, Type="Service", Name=product.account_name, qb=client,
    )
    if item:
        item = item[0]
    else:
        item = Item()
        item.Name = product.account_name
        item.Type = "Service"
        item.IncomeAccountRef = account
        item.save(qb=client)
    return item


def get_default_terms():
    term = Term.filter(max_results=1, Name="Due on Receipt", qb=client,)
    if term:
        term = term[0]
    else:
        term = Term()
        term.Name = "Due on Receipt"
        term.save(qb=client)
    return term


def save_invoice(order):
    customer = get_customer(order.student)
    invoice = Invoice.filter(max_results=1, DocNumber=order.number, qb=client)
    if invoice:
        invoice = invoice[0]
    else:
        invoice = Invoice()
        invoice.DocNumber = order.number

    invoice.CustomerRef = customer.to_ref()
    invoice.DueDate = order.date_paid
    # Term does not have a to_ref method, go figure, so we manually generate this value
    invoice.SalesTermRef = {"value": get_default_terms().Id}

    orderlineitem_set = list(order.orderlineitem_set.all())
    for i, l in enumerate(invoice.Line):
        try:
            l.Amount = orderlineitem_set[i].total_charge
            l.Description = orderlineitem_set[i].product.name
            item = get_item(orderlineitem_set[i].product)
            l.SalesItemLineDetail.ItemRef = item.to_ref()
            l.SalesItemLineDetail.ServiceDate = order.date_paid
            l.SalesItemLineDetail.Qty = orderlineitem_set[i].qty
            l.SalesItemLineDetail.UnitPrice = orderlineitem_set[i].charge
            l.save()
        except IndexError:  # the order has been updated to remove a line item
            l.delete(qb=client)

    if len(orderlineitem_set) > len(invoice.Line):  # the order has been updated or created to add line items
        for l in orderlineitem_set[len(invoice.Line):]:
            line = SalesItemLine()
            line.Amount = l.total_charge
            line.Description = l.product.name
            line.SalesItemLineDetail = SalesItemLineDetail()
            item = get_item(l.product)
            line.SalesItemLineDetail.ItemRef = item.to_ref()
            line.SalesItemLineDetail.ServiceDate = order.date_paid
            line.SalesItemLineDetail.Qty = l.qty
            line.SalesItemLineDetail.UnitPrice = l.charge
            invoice.Line.append(line)

    invoice.save(qb=client)
    return invoice

# Monkey patch the third-party library that doesn't handle JSON conversion correctly for datetimes

from quickbooks import mixins


def new_json_filter(self):
    """
    filter out properties that have names starting with _
    or properties that have a value of None
    """
    def f(obj):
        if isinstance(obj, datetime.date) or isinstance(obj, datetime.datetime):
            return str(obj)
        else:
            return dict((k, v) for k, v in obj.__dict__.items()
                   if not k.startswith('_') and getattr(obj, k) is not None)
    return f


mixins.ToJsonMixin.json_filter = new_json_filter

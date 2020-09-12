from bot.models import WithdrawalRequest
import logging


def verification_withdrawal_requests():
    withdrawal_requests = WithdrawalRequest.objects.filter(status='pending verification')

    request_list = []
    for r in withdrawal_requests:
        r.status = 'verifed'
        r.type_withdrawal = 'manual'
        request_list.append(r)

    WithdrawalRequest.objects.bulk_update(request_list, ['status', 'type_withdrawal'])
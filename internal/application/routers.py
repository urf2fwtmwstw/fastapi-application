from internal.controllers import categories, transactions


def handlers(app):
    app.include_router(categories.router, prefix="/api/v1/categories")
    app.include_router(transactions.router, prefix="/api/v1/transactions")
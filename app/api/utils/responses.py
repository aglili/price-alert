from fastapi.responses import ORJSONResponse


def send_data_with_info(data, info: str, status_code: int = 200):
    return ORJSONResponse(
        status_code=status_code,
        content={
            "info": info,
            "data": data,
        },
    )


def internal_server_error(user_msg: str, error, status_code: int = 500):
    return ORJSONResponse(
        status_code=status_code,
        content={
            "userMsg": user_msg,
            "devMsg": str(error),
        },
    )


def client_side_error(user_msg: str, status_code: int = 400):
    return ORJSONResponse(
        status_code=status_code,
        content={
            "userMsg": user_msg,
            "devMsg": user_msg,
        },
    )


def send_info(info, status_code: int = 200):
    return ORJSONResponse(
        status_code=status_code,
        content={
            "info": info,
        },
    )

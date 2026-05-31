# from app.models.chat import ChatMessage


# def get_conversation(db, session_id):
#     return (
#         db.query(ChatMessage)
#         .filter(ChatMessage.session_id == session_id)
#         .order_by(ChatMessage.created_at.asc())
#         .all()
#     )


# def save_message(
#     db,
#     session_id,
#     role,
#     content
# ):
#     msg = ChatMessage(
#         session_id=session_id,
#         role=role,
#         content=content
#     )

#     db.add(msg)
#     db.commit()


from app.models.chat import ChatMessage, ChatSession


def get_conversation(db, session_id):
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


def create_session_if_not_exists(
    db,
    session_id,
    user_id
):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id)
        .first()
    )

    if not session:
        session = ChatSession(
            id=session_id,
            user_id=user_id
        )

        db.add(session)
        db.commit()

    return session


def save_message(
    db,
    session_id,
    role,
    content
):
    msg = ChatMessage(
        session_id=session_id,
        role=role,
        content=content
    )

    db.add(msg)
    db.commit()
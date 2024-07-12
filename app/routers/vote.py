from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import schemas, oauth2, models, database
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/vote")
def vote(vote: schemas.Vote, db: Session = Depends(database.get_db), current_user: int = Depends(oauth2.get_current_user)):

    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    vote_found = vote_query.first()

    booms = db.query(models.Post).filter(models.Post.id == vote.post_id).first
    if not booms:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with an id: {vote.post_id}was not found")

    if (vote.dir == 1):
        if vote_found:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user{current_user.id} has already voted on post {vote.post_id}")

        new_vote = models.Vote(post_id = vote.post_id, user_id=current_user.id)
        db.add(new_vote)
        db.commit()
        return {"message": "Successfully added vote"}
    else:
        if not vote_found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote doesn't exist")

        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message": "vote removed successfully"}



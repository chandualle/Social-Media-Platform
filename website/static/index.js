function like(postId) {
  const likeCount = document.getElementById(`likes-count-${postId}`);
  const likeButton = document.getElementById(`like-button-${postId}`);

  fetch(`/like-post/${postId}`, { method: "POST" })
    .then((res) => res.json())
    .then((data) => {
      likeCount.innerHTML = data["likes"];
      if (data["liked"] === true) {
        likeButton.className = "fas fa-thumbs-up";
      } else {
        likeButton.className = "far fa-thumbs-up";
      }
    })
    .catch((e) => alert("Could not like post."));
}
    function toggleTotalText(button) {
        const postDescription = button.parentElement;
        const modal = postDescription.querySelector('.modal');
        const overlay = postDescription.querySelector('.overlay');

        modal.style.display = (modal.style.display === 'none') ? 'block' : 'none';
        overlay.style.display = (overlay.style.display === 'none') ? 'block' : 'none';
    }

    function closeModal() {
        const overlays = document.querySelectorAll('.overlay');
        const modals = document.querySelectorAll('.modal');

        overlays.forEach((overlay) => {
            overlay.style.display = 'none';
        });

        modals.forEach((modal) => {
            modal.style.display = 'none';
        });
    }

 // Function to update character count for the textarea
function updateCharCount(textAreaId, countSpanId, maxLimit) {
  const textArea = document.getElementById(textAreaId);
  const countSpan = document.getElementById(countSpanId);

  textArea.addEventListener('input', function () {
    const count = textArea.value.length;
    countSpan.textContent = count + '/' + maxLimit;

    // If you want to change color when limit is exceeded
    if (count > maxLimit) {
      countSpan.style.color = 'red';
    } else {
      countSpan.style.color = '#999';
    }
  });
}
$(document).ready(function() {
    $('.like-post').click(function(e) {
        e.preventDefault();
        var postID = $(this).data('post-id');
        var likeButton = $(this); // Store the like button element

        $.ajax({
            type: 'POST',
            url: '/like-post/' + postID,
            success: function(response) {
                console.log(response); // Log the response if needed

                // Update the UI to reflect the like action
                var updatedLikesCount = response.likes; // Ensure 'likes' matches the property name from your Flask route
                if (updatedLikesCount >= 2) {
                    // Update the like button text if the like count reaches 2 or more
                    likeButton.html('Not a Dream, Remove It (2 likes reached)');
                } else {
                    // Update the like button text with the new like count
                    likeButton.html('Not a Dream, Remove It<br/>' + updatedLikesCount + '/2');
                }
            },
            error: function(error) {
                console.error('Error:', error);
            }
        });
    });

    $('.delete-post').click(function(e) {
        e.preventDefault();
        var postID = $(this).data('post-id');
        var postElement = $(this).closest('.post');

        $.ajax({
            type: 'GET',
            url: '/delete-post/' + postID,
            success: function(response) {
                console.log(response); // Log the response if needed

                // Remove the deleted post from the UI
                postElement.remove();
            },
            error: function(error) {
                console.error('Error:', error);
            }
        });
    });
});

$(document).ready(function() {
    $('.like-post').click(function(e) {
        e.preventDefault();

        var postId = $(this).data('post-id');
        var postContainer = $('#post-' + postId);
        var notificationText = postContainer.find('.notification-text');

        // Show the notification text
        notificationText.show();

        // Hide the text after 4 seconds
        setTimeout(function() {
            notificationText.hide();
        }, 4000);
    });
});

function toggleFollow(userId) {
    fetch(`/toggle-follow/${userId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update the UI based on the response
            const followButton = document.getElementById(`follow-${userId}`);
            const unfollowButton = document.getElementById(`unfollow-${userId}`);

            if (followButton && unfollowButton) {
                if (data.following) {
                    followButton.style.display = 'none';
                    unfollowButton.style.display = 'inline-block';
                } else {
                    followButton.style.display = 'inline-block';
                    unfollowButton.style.display = 'none';
                }
            }
        } else {
            // Handle errors or display a message if needed
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

    $(document).ready(function() {
    $('.save-post').click(function(e) {
        e.preventDefault();

        var postId = $(this).data('post-id');
        var saveButton = $(this);

        $.ajax({
            type: 'GET',
            url: '/save-post/' + postId,
            success: function(response) {
                console.log(response); // Log the response if needed

                // Toggle button text and class based on the response
                if (saveButton.text().trim() === 'Save') {
                    saveButton.text('Unsave');
                    // Optionally, update other styles or classes
                } else {
                    saveButton.text('Save');
                    // Optionally, update other styles or classes
                }
            },
            error: function(error) {
                console.error('Error:', error);
            }
        });
    });
});
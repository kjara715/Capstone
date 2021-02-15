//logic to hide or show recipe details by clicking View Recipe Button
$(document).ready(function(){

    $(".card-text").hide()
    $(".comment-form").hide()

    $(document).on("click", ".recipe", function(){

        //change button name depending on if recipe is showing or hidden (starts hidden)
        if($(this).text() === "View Recipe"){
            $(this).text("Hide Recipe")
        } else {
            $(this).text("View Recipe")
        }
        
        //show and hide recipe on each button click
        $(this).parent().children('.card-text').toggle()
        
    });

    $(document).on("click", ".comment", function(){

        $(this).parent().children(".comment-form").toggle()

    })


  });

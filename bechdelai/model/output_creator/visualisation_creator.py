def show_embeddings2D(self,embeddings2D,faces = None,size = 0.5,opacity = 0.8):

        # Plot scatter plot

        if "cluster" in embeddings2D.columns:
            fig = px.scatter(
                embeddings2D.assign(size = lambda x : 20),
                x="x",
                y="y",
                color="cluster",
                size = "size"
            )
        else:
            fig = px.scatter(
                embeddings2D,
                x="x",
                y="y",
            )

        # Add faces
        if faces is not None:

            for i, face in enumerate(faces):
                row = embeddings2D.iloc[i]
                fig.add_layout_image(
                    dict(
                        source=face.img,
                        xref="x",
                        yref="y",
                        xanchor="center",
                        yanchor="middle",
                        x=row["x"],
                        y=row["y"],
                        sizex = size,
                        sizey = size,
            #             sizex=np.sqrt(row["pop"] / df["pop"].max()) * maxi * 0.2 + maxi * 0.05,
            #             sizey=np.sqrt(row["pop"] / df["pop"].max()) * maxi * 0.2 + maxi * 0.05,
                        sizing="contain",
                        opacity=opacity,
                        # layer="above"
                    )
                )

            # fig.update_layout(height=600, width=1000,, plot_bgcolor="#dfdfdf")
            fig.show()
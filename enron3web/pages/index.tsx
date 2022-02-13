import type { NextPage } from 'next'
import Head from 'next/head'
import Image from 'next/image'
import { Navbar, Container, Nav, Row, Badge, Button, Card, Col, ListGroup, ProgressBar } from 'react-bootstrap'
import styles from '../styles/Home.module.css'
import { HiOutlineLocationMarker } from "react-icons/hi";
import { MdRestartAlt } from "react-icons/md";
import { db, initFirebase } from '../lib/initFirebase'
import { useEffect, useState } from 'react'
import { collection, doc, getDoc, getDocs, query, setDoc, where } from 'firebase/firestore'
import axios, { AxiosRequestConfig } from 'axios'
import TitleLogo from "../public/enronLogo.svg";


const Home: NextPage = ({children}) => {  
  
  const [trashCanIncoming, setTrashCanIncoming] = useState(children)

  useEffect( () => {
    setInterval( () => {getTrashCanData()}, 30000);
  }, [])

  const getTrashCanData = () => {
    const config: AxiosRequestConfig = {
        method: "get",
        url: `/api/container/getAll`,
        headers: {
            "Content-Type": "application/json",
        },
    };

    try {
      
          axios(config).catch( () => {
          }).then( response => {
              if (response && response.status === 200 ) {
                setTrashCanIncoming(response.data)        
              }
          });

    } catch (err) {
        console.error(err);
    }
  }

  const TrashCanList = ({trashCans}: any) => {
    const TrashCansArray = trashCans.map( (trashCan: any) => {

        const cardVariant = (trashCan.capacity >= 100) ? "danger" : "primary";

        const resetTrashCan = async () => {

          const config: AxiosRequestConfig = {
              method: "post",
              url: `/api/container/post/${trashCan.id}/0`,
              headers: {
                  "Content-Type": "application/json",
              },
          };
  
          try {
             
                axios(config).catch( () => {

                }).then( response => {
                    if (response && response.status === 200 ) {
                      getTrashCanData()         
                    }
                });
  
          } catch (err) {
              console.error(err);
          }
      };

        return (
            <Col key={trashCan}>
                <Card  className={`${styles.projectCard} `} >
                    <div  className={`${styles.projectBadge} `}>
                       {  (trashCan.capacity >= 100) ? <Badge  className={`${styles.projectBadge} `} bg="danger">Full</Badge> : <></> }
                    </div>
                    <ListGroup variant="flush">

                        <ListGroup.Item>
                        <div  className={`d-flex justify-content-end`}>
                            <MdRestartAlt className="" onClick={() => resetTrashCan()}/>

                        </div>
                            <ProgressBar className={`${styles.projectProgress} mt-5 mb-1`} striped animated={(trashCan.capacity >= 100)} variant={cardVariant}  now={trashCan.capacity}  label={`${trashCan.capacity}%`} />
                            <Card.Text>
                            <HiOutlineLocationMarker className="mb-1"/>
                                {trashCan.location}
                            </Card.Text>

                        </ListGroup.Item>
                        <ListGroup.Item>
                            <Card.Title>Container #{trashCan.id}</Card.Title>
                            <Button  className="text-uppercase font-weight-bold" variant={cardVariant} href={trashCan.direction}>Get Direction</Button>
                        </ListGroup.Item>

                    </ListGroup>
                </Card>
            </Col>
        );
    }
    );

    
    return (
      <Row md={4} className=" mb-2 mt-0 g-4">
          {TrashCansArray}
      </Row>
      );
    };

    
  //   const trashCanIncoming = [
  //     {
  //         id: 1,
  //         capacity: 50,
  //         location: 'Polytechnique Montréal',
  //         direction: "https://goo.gl/maps/gxvtnHtas3inFKWU9"
  //     },
  //     {
  //       id: 2,
  //       capacity: 100,
  //       location: '2700 Ch de la Tour',
  //       direction: "https://goo.gl/maps/t6Pbx348vX8AyM1Z9"
  //   },
  // ];

  return (

    <div >

    <Navbar bg="light" variant="light">
    <Container>
      <Navbar.Brand href="#home">
      <Image src={TitleLogo} alt="" width={'120px'} height={'120px'}/>

      </Navbar.Brand>
    </Container>
    </Navbar>

    <Container>

    <TrashCanList trashCans={trashCanIncoming}/>

    </Container>
      
    </div>  
  )
}

export async function getServerSideProps() {

  const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/container/getAll`)
  const children= await res.json()
  console.log(children);

  return { props: { children } }
}



export default Home


